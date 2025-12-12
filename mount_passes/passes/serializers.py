from rest_framework import serializers
from .models import User, Coords, Level, MountainPass, PassImage
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def validate_phone(self, value):
        """Проверка формата телефона"""
        if not value.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
            raise serializers.ValidationError("Некорректный формат телефона")
        return value


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class PassImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassImage
        fields = ['title', 'image']


class MountainPassSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PassImageSerializer(many=True)

    class Meta:
        model = MountainPass
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect',
            'user', 'coords', 'level', 'images', 'add_time', 'status'
        ]
        read_only_fields = ['add_time', 'status']

    def create(self, validated_data):
        # Извлекаем вложенные данные
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images')

        # Создаем или получаем пользователя
        user, _ = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )

        # Создаем координаты
        coords = Coords.objects.create(**coords_data)

        # Создаем уровень сложности
        level = Level.objects.create(**level_data)

        # Создаем перевал
        mountain_pass = MountainPass.objects.create(
            user=user,
            coords=coords,
            level=level,
            **validated_data
        )

        # Добавляем изображения
        for image_data in images_data:
            image = PassImage.objects.create(**image_data)
            mountain_pass.images.add(image)

        return mountain_pass

    def update(self, instance, validated_data):
        # Обновление перевала (для модерации)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class MountainPassUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса"""

    class Meta:
        model = MountainPass
        fields = ['status']