from django.contrib import admin
from .models import Contact

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
