from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informazioni aggiuntive', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informazioni aggiuntive', {'fields': ('role',)}),
    )
