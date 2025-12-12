from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(models.Model):
    """Модель пользователя (туриста)"""
    email = models.EmailField(unique=True, verbose_name="Email")
    fam = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    otc = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.fam} {self.name} ({self.email})"


class Coords(models.Model):
    """Модель географических координат"""
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Широта",
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Долгота",
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    height = models.IntegerField(
        verbose_name="Высота",
        validators=[MinValueValidator(0), MaxValueValidator(9000)]
    )

    class Meta:
        verbose_name = "Координаты"
        verbose_name_plural = "Координаты"

    def __str__(self):
        return f"({self.latitude}, {self.longitude}), высота: {self.height}м"


class Level(models.Model):
    """Модель уровня сложности в разные времена года"""
    LEVEL_CHOICES = [
        ('1A', '1А'),
        ('1B', '1Б'),
        ('2A', '2А'),
        ('2B', '2Б'),
        ('3A', '3А'),
        ('3B', '3Б'),
    ]

    winter = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Зима"
    )
    summer = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Лето"
    )
    autumn = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Осень"
    )
    spring = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Весна"
    )

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"

    def __str__(self):
        seasons = []
        for season in ['winter', 'summer', 'autumn', 'spring']:
            level = getattr(self, season)
            if level:
                seasons.append(f"{season}: {level}")
        return ", ".join(seasons) if seasons else "Не указано"


class MountainPass(models.Model):
    """Основная модель перевала"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('pending', 'На модерации'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    beauty_title = models.CharField(max_length=255, verbose_name="Тип объекта")
    title = models.CharField(max_length=255, verbose_name="Название")
    other_titles = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Другое название"
    )
    connect = models.TextField(blank=True, null=True, verbose_name="Соединяет")

    # Внешние ключи
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passes',
        verbose_name="Пользователь"
    )
    coords = models.OneToOneField(
        Coords,
        on_delete=models.CASCADE,
        related_name='pass',
        verbose_name="Координаты"
    )
    level = models.OneToOneField(
        Level,
        on_delete=models.CASCADE,
        related_name='pass',
        verbose_name="Уровень сложности"
    )

    # Поля перевала
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="Время добавления")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )

    # Дополнительные поля
    images = models.ManyToManyField(
        'PassImage',
        related_name='passes',
        verbose_name="Изображения"
    )

    class Meta:
        verbose_name = "Перевал"
        verbose_name_plural = "Перевалы"
        ordering = ['-add_time']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class PassImage(models.Model):
    """Модель для изображений перевала"""
    title = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(upload_to='pass_images/', verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Изображение перевала"
        verbose_name_plural = "Изображения перевалов"

    def __str__(self):
        return self.title