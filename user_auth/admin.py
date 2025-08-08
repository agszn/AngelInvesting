from django.contrib import admin
from .models import Contact

# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict editing of user_type to superusers
        if not self.current_user.is_superuser:
            self.fields['user_type'].disabled = True

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user  # pass the request user to form
        return form

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'otp', 'user_type'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')  # Displays these fields in the admin list view
    search_fields = ('name', 'email')  # Enables search functionality
    list_filter = ('email',)  # Adds filtering by email


from django.contrib import admin
from .models import Broker

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('broker_id', 'name')
    search_fields = ('broker_id', 'name')


from django.contrib import admin
from .models import FAQ_G
# ------------- G User FAQ -------------
@admin.register(FAQ_G)
class FAQGUser(admin.ModelAdmin):
    list_display = ['title', 'style', 'created_at']
    search_fields = ['title', 'subtitle']
    list_filter = ['style', 'created_at']

    class Media:
        js = ('js/faq_style.js',)