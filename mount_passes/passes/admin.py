from django.contrib import admin
from .models import User, Coords, Level, MountainPass, PassImage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'fam', 'name', 'phone')
    search_fields = ('email', 'fam', 'name')


@admin.register(Coords)
class CoordsAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'height')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('winter', 'summer', 'autumn', 'spring')


@admin.register(PassImage)
class PassImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')


@admin.register(MountainPass)
class MountainPassAdmin(admin.ModelAdmin):
    list_display = ('title', 'beauty_title', 'user', 'status', 'add_time')
    list_filter = ('status', 'add_time')
    search_fields = ('title', 'beauty_title', 'user__email')
    readonly_fields = ('add_time',)
    filter_horizontal = ('images',)
