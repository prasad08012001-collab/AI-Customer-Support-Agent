
from django.contrib import admin
from .models import Conversation, ChatMessage, Ticket, Order


# Customer Conversation Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "customer_email",
        "subject",
        "status",
        "created_at",
    )

    list_filter = ("status",)

    search_fields = (
        "customer_name",
        "customer_email",
        "subject",
    )

    list_editable = ("status",)

    readonly_fields = ("created_at",)


# Customer Chat Message Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "session_key",
        "message_type",
        "message",
        "created_at",
    )

    list_filter = ("message_type",)

    search_fields = (
        "session_key",
        "message",
    )

    readonly_fields = ("created_at",)


# Customer Support Ticket Admin
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "customer_email",
        "subject",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "customer_name",
        "customer_email",
        "subject",
    )

    list_editable = ("status",)

    readonly_fields = ("created_at", "updated_at")


# Customer Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "customer_name",
        "customer_email",
        "product_name",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "order_id",
        "customer_name",
        "customer_email",
        "product_name",
    )

    list_editable = ("status",)

    readonly_fields = ("created_at", "updated_at")
