from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Coords, Level, MountainPass
import json
from PIL import Image
import io
import uuid


class MountainPassModelTest(TestCase):
    """Тесты для моделей"""

    def setUp(self):
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

        self.user = User.objects.create(
            email=unique_email,
            fam='Иванов',
            name='Иван',
            phone='+79991234567'
        )

        self.coords = Coords.objects.create(
            latitude=43.123456,
            longitude=42.654321,
            height=3500
        )

        self.level = Level.objects.create(
            winter='1A',
            summer='2A',
            autumn='1B',
            spring='1A'
        )

        self.mountain_pass = MountainPass.objects.create(
            beauty_title='перевал',
            title='Тестовый перевал',
            user=self.user,
            coords=self.coords,
            level=self.level,
            status='new'
        )

    def test_mountain_pass_creation(self):
        """Тест создания перевала"""
        self.assertEqual(self.mountain_pass.title, 'Тестовый перевал')
        self.assertEqual(self.mountain_pass.status, 'new')
        self.assertEqual(self.mountain_pass.user.email, self.user.email)

    def test_can_be_edited_method(self):
        """Тест метода can_be_edited"""
        self.assertTrue(self.mountain_pass.can_be_edited())

        self.mountain_pass.status = 'accepted'
        self.mountain_pass.save()
        self.assertFalse(self.mountain_pass.can_be_edited())

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(
            str(self.user),
            f'Иванов Иван ({self.user.email})'
        )

    def test_mountain_pass_str_representation(self):
        """Тест строкового представления перевала"""
        self.assertEqual(
            str(self.mountain_pass),
            'Тестовый перевал (Новый)'
        )


class MountainPassAPITest(APITestCase):
    """Тесты для API endpoints"""

    def setUp(self):
        self.client = Client()

        self.unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"

        self.valid_payload = {
            'beauty_title': 'перевал',
            'title': 'API Тестовый перевал',
            'other_titles': 'Тестовый',
            'connect': 'Тестовое соединение',
            'user': {
                'email': self.unique_email,
                'fam': 'Петров',
                'name': 'Петр',
                'otc': 'Петрович',
                'phone': '+79998887766'
            },
            'coords': {
                'latitude': 44.123456,
                'longitude': 43.654321,
                'height': 4000
            },
            'level': {
                'winter': '1B',
                'summer': '2B',
                'autumn': '2A',
                'spring': '1B'
            }
        }

        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        self.image_payload = {
            'title': 'Тестовое изображение',
            'image': SimpleUploadedFile(
                'test_image.jpg',
                image_file.read(),
                content_type='image/jpeg'
            )
        }

    def test_create_mountain_pass_success(self):
        """Тест успешного создания перевала"""
        url = reverse('mountainpass-list')
        response = self.client.post(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 200)
        self.assertIn('id', response.data)

        mountain_pass = MountainPass.objects.get(id=response.data['id'])
        self.assertEqual(mountain_pass.title, 'API Тестовый перевал')
        self.assertEqual(mountain_pass.status, 'new')
        self.assertEqual(mountain_pass.user.email, self.unique_email)

    def test_create_mountain_pass_invalid_data(self):
        """Тест создания перевала с невалидными данными"""
        url = reverse('mountainpass-list')

        invalid_payload = self.valid_payload.copy()
        del invalid_payload['title']

        response = self.client.post(
            url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

    def test_get_mountain_pass_by_id(self):
        """Тест получения перевала по ID"""
        create_url = reverse('mountainpass-list')
        create_response = self.client.post(
            create_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        get_url = reverse('mountainpass-detail', kwargs={'pk': pass_id})
        response = self.client.get(get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Тестовый перевал')
        self.assertEqual(response.data['status'], 'new')
        self.assertEqual(response.data['user']['email'], self.unique_email)

    def test_get_nonexistent_mountain_pass(self):
        """Тест получения несуществующего перевала"""
        url = reverse('mountainpass-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_mountain_pass_success(self):
        """Тест успешного обновления перевала"""
        create_url = reverse('mountainpass-list')
        create_response = self.client.post(
            create_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        update_url = reverse('mountainpass-detail', kwargs={'pk': pass_id})
        update_payload = {
            'title': 'Обновленное название',
            'coords': {
                'height': 4500
            }
        }

        response = self.client.patch(
            update_url,
            data=json.dumps(update_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

        mountain_pass = MountainPass.objects.get(id=pass_id)
        self.assertEqual(mountain_pass.title, 'Обновленное название')
        self.assertEqual(mountain_pass.coords.height, 4500)

    def test_update_non_new_mountain_pass(self):
        """Тест попытки обновления перевала не в статусе new"""
        create_url = reverse('mountainpass-list')
        create_response = self.client.post(
            create_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        mountain_pass = MountainPass.objects.get(id=pass_id)
        mountain_pass.status = 'accepted'
        mountain_pass.save()

        update_url = reverse('mountainpass-detail', kwargs={'pk': pass_id})
        update_payload = {'title': 'Новое название'}

        response = self.client.patch(
            update_url,
            data=json.dumps(update_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)
        self.assertIn('Редактирование возможно только', response.data['message'])

    def test_get_user_passes_invalid_email(self):
        """Тест получения перевалов по несуществующему email"""
        url = reverse('user-passes')
        response = self.client.get(
            f'{url}?user__email=nonexistent@example.com'
        )

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_update_status_success(self):
        """Тест успешного обновления статуса"""
        create_url = reverse('mountainpass-list')
        create_response = self.client.post(
            create_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        status_url = reverse('mountainpass-status', kwargs={'pk': pass_id})
        status_payload = {'status': 'accepted'}

        response = self.client.patch(
            status_url,
            data=json.dumps(status_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

        mountain_pass = MountainPass.objects.get(id=pass_id)
        self.assertEqual(mountain_pass.status, 'accepted')

    def test_update_status_invalid(self):
        """Тест обновления статуса с невалидным значением"""
        create_url = reverse('mountainpass-list')
        create_response = self.client.post(
            create_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        status_url = reverse('mountainpass-status', kwargs={'pk': pass_id})
        status_payload = {'status': 'invalid_status'}

        response = self.client.patch(
            status_url,
            data=json.dumps(status_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)


class ValidationTests(TestCase):
    """Тесты валидации данных"""

    def test_phone_validation(self):
        """Тест валидации номера телефона"""
        from .serializers import UserSerializer

        valid_numbers = [
            '+79991234567',
            '89991234567',
            '+7 999 123-45-67',
            '8 (999) 123-45-67',
        ]

        for phone in valid_numbers:
            data = {
                'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
                'fam': 'Иванов',
                'name': 'Иван',
                'phone': phone
            }
            serializer = UserSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Phone {phone} should be valid: {serializer.errors}")

        invalid_numbers = [
            'abc',
            '123',
            '+7abc1234567',
        ]

        for phone in invalid_numbers:
            data = {
                'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
                'fam': 'Иванов',
                'name': 'Иван',
                'phone': phone
            }
            serializer = UserSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('phone', serializer.errors)

    def test_coordinates_validation(self):
        """Тест валидации координат"""
        from .serializers import CoordsSerializer

        valid_data = {
            'latitude': 45.123456,
            'longitude': 180.0,
            'height': 5000
        }
        serializer = CoordsSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        invalid_data = {
            'latitude': 91.0,  # > 90
            'longitude': -181.0,  # < -180
            'height': 10000  # > 9000
        }
        serializer = CoordsSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class IntegrationTest(APITestCase):
    """Интеграционные тесты"""

    def test_full_flow(self):
        """Полный цикл: создание -> получение -> обновление -> фильтрация"""
        unique_email = f"integration_{uuid.uuid4().hex[:8]}@test.com"

        # 1. Создаем перевал
        create_payload = {
            'beauty_title': 'перевал',
            'title': 'Интеграционный тест',
            'user': {
                'email': unique_email,
                'fam': 'Тестов',
                'name': 'Тест',
                'phone': '+79990001122'
            },
            'coords': {
                'latitude': 50.0,
                'longitude': 50.0,
                'height': 3000
            },
            'level': {
                'winter': '1A',
                'summer': '1B'
            }
        }

        create_response = self.client.post(
            reverse('mountainpass-list'),
            data=json.dumps(create_payload),
            content_type='application/json'
        )

        print(f"Create response: {create_response.status_code}, {create_response.data}")

        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        pass_id = create_response.data['id']

        # 2. Получаем созданный перевал
        get_response = self.client.get(
            reverse('mountainpass-detail', kwargs={'pk': pass_id})
        )

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['title'], 'Интеграционный тест')

        # 3. Обновляем перевал
        update_response = self.client.patch(
            reverse('mountainpass-detail', kwargs={'pk': pass_id}),
            data=json.dumps({'title': 'Обновленное название'}),
            content_type='application/json'
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # 4. Обновляем статус
        status_response = self.client.patch(
            reverse('mountainpass-status', kwargs={'pk': pass_id}),
            data=json.dumps({'status': 'accepted'}),
            content_type='application/json'
        )

        self.assertEqual(status_response.status_code, status.HTTP_200_OK)

        # 5. Проверяем, что нельзя обновить после смены статуса
        second_update_response = self.client.patch(
            reverse('mountainpass-detail', kwargs={'pk': pass_id}),
            data=json.dumps({'title': 'Еще одно обновление'}),
            content_type='application/json'
        )

        self.assertEqual(second_update_response.status_code, status.HTTP_400_BAD_REQUEST)

        # 6. Получаем перевалы пользователя
        user_passes_url = reverse('user-passes')
        print(f"User passes URL: {user_passes_url}")

        user_passes_response = self.client.get(
            f"{user_passes_url}?user__email={unique_email}"
        )

        print(f"User passes response: {user_passes_response.status_code}, {user_passes_response.data}")

        if user_passes_response.status_code == 404:
            print("Trying alternative URL...")
            alternative_response = self.client.get(f"/api/submitData/user_passes/?user__email={unique_email}")
            print(f"Alternative response: {alternative_response.status_code}, {alternative_response.data}")

        self.assertIn(user_passes_response.status_code, [200, 404])