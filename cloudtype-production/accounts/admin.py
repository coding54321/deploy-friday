from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cafe
from .forms import CafeCreationForm, CafeChangeForm

class CafeAdmin(UserAdmin):
    add_form = CafeCreationForm
    form = CafeChangeForm
    model = Cafe
    list_display = ('cafe_id', 'cafe_name', 'telephone', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('cafe_id', 'password', 'cafe_photo')}),
        ('Personal info', {'fields': ('cafe_name', 'telephone', 'ceo_name', 'cafe_time', 'ceo_tel', 'cafe_region', 'cafe_tel', 'cafe_address', 'seats_count', 'latitude', 'longitude', 'email')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active', 'is_guest')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cafe_id', 'cafe_name', 'telephone', 'password1', 'password2', 'cafe_photo', 'is_superuser')}
        ),
    )
    search_fields = ('cafe_id',)
    ordering = ('cafe_id',)

admin.site.register(Cafe, CafeAdmin)
