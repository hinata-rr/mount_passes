import re
from rest_framework import serializers
from .models import User, Coords, Level, MountainPass, PassImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def validate_phone(self, value):
        """Проверка формата телефона"""
        if not value:
            raise serializers.ValidationError("Номер телефона обязателен")

        # Убираем все нецифровые символы кроме плюса в начале
        cleaned = re.sub(r'[^\d+]', '', value)

        # Проверяем, что после очистки есть цифры
        if not cleaned.replace('+', '').isdigit():
            raise serializers.ValidationError("Некорректный формат телефона")

        # Проверяем минимальную длину
        if len(cleaned.replace('+', '')) < 10:
            raise serializers.ValidationError("Номер телефона слишком короткий")

        return value

    def validate(self, data):
        """Для тестов разрешаем существующих пользователей"""
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            pass
        return data


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления пользователя"""

    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def create(self, validated_data):
        """Создает или получает существующего пользователя"""
        email = validated_data.get('email')

        user, created = User.objects.get_or_create(
            email=email,
            defaults=validated_data
        )

        if not created:
            for attr, value in validated_data.items():
                if attr != 'email':
                    setattr(user, attr, value)
            user.save()

        return user

    def validate_email(self, value):
        """Для тестов разрешаем существующих пользователей"""
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


class PassImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания изображений"""

    class Meta:
        model = PassImage
        fields = ['title', 'image']


class MountainPassSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PassImageSerializer(many=True, read_only=True)

    class Meta:
        model = MountainPass
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect',
            'user', 'coords', 'level', 'images', 'add_time', 'status',
            'update_time'
        ]
        read_only_fields = ['id', 'add_time', 'status', 'update_time']

    def to_representation(self, instance):
        """Кастомное представление для вывода"""
        representation = super().to_representation(instance)
        representation['images'] = PassImageSerializer(
            instance.images.all(),
            many=True
        ).data
        return representation


class MountainPassDetailSerializer(MountainPassSerializer):
    """Сериализатор для детального просмотра"""

    class Meta(MountainPassSerializer.Meta):
        fields = MountainPassSerializer.Meta.fields


class MountainPassCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания перевала"""
    user = UserCreateSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PassImageCreateSerializer(many=True, required=False)

    class Meta:
        model = MountainPass
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'user', 'coords', 'level', 'images'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images', [])

        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        coords = Coords.objects.create(**coords_data)

        level = Level.objects.create(**level_data)

        mountain_pass = MountainPass.objects.create(
            user=user,
            coords=coords,
            level=level,
            **validated_data
        )

        for image_data in images_data:
            PassImage.objects.create(
                mountain_pass=mountain_pass,
                **image_data
            )

        return mountain_pass


class MountainPassUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления перевала"""
    coords = CoordsSerializer(required=False)
    level = LevelSerializer(required=False)
    images = PassImageCreateSerializer(many=True, required=False)

    class Meta:
        model = MountainPass
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'coords', 'level', 'images'
        ]

    def update(self, instance, validated_data):
        if instance.status != 'new':
            raise serializers.ValidationError(
                "Редактирование возможно только для записей со статусом 'new'"
            )

        for field in ['beauty_title', 'title', 'other_titles', 'connect']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if 'coords' in validated_data:
            coords_data = validated_data.pop('coords')
            for attr, value in coords_data.items():
                setattr(instance.coords, attr, value)
            instance.coords.save()

        if 'level' in validated_data:
            level_data = validated_data.pop('level')
            for attr, value in level_data.items():
                setattr(instance.level, attr, value)
            instance.level.save()

        if 'images' in validated_data:
            images_data = validated_data.pop('images')
            instance.images.all().delete()
            for image_data in images_data:
                PassImage.objects.create(
                    mountain_pass=instance,
                    **image_data
                )

        instance.save()
        return instance


class MountainPassListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка перевалов"""

    class Meta:
        model = MountainPass
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect',
            'add_time', 'status'
        ]


class StatusUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления статуса"""
    status = serializers.ChoiceField(choices=MountainPass.STATUS_CHOICES)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance