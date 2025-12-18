from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Room, RoomImage, Booking


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("phone_number",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + ((None, {"fields": ("phone_number",)}),)
    list_display = ("username", "email", "phone_number", "is_staff", "is_superuser")


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "price_per_night", "max_guests", "is_available")
    search_fields = ("name", "description", "slug")
    list_filter = ("is_available",)
    inlines = [RoomImageInline]


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ("room", "image", "is_primary", "created_at")
    list_filter = ("is_primary", "room")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "room", "guest_name", "guest_phone", "guest_email", "check_in", "check_out", "guests", "total_amount", "status", "created_at")
    search_fields = ("reference", "room__name", "guest_name", "guest_email", "guest_phone")
    list_filter = ("status", "room")
    autocomplete_fields = ("room", "user")
    readonly_fields = ("reference", "created_at", "updated_at")
    ordering = ("-created_at",)
