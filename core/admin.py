from django.contrib import admin
from .models import User, Product, Sales
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.register(Product)
admin.site.register(Sales)

class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff',)

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'is_staff',
                'password',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'is_staff',
                'password1',
                'password2',
            ),
        }),
    )


admin.site.register(User, UserAdmin)