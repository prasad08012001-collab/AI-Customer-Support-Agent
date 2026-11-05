from django.urls import path
from . import views


urlpatterns = [

    # Dashboard
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # Customer Chat
    path(
        "chat/",
        views.chat,
        name="chat"
    ),

    # Clear Customer Chat
    path(
        "clear-chat/",
        views.clear_chat,
        name="clear_chat"
    ),

    # Chat History
    path(
        "chat-history/",
        views.chat_history,
        name="chat_history"
    ),

    # Individual Customer Chat History
    path(
        "chat-history/<str:session_key>/",
        views.customer_chat_history,
        name="customer_chat_history"
    ),

    # Ticket Creation
    path(
        "create-ticket/",
        views.create_ticket,
        name="create_ticket"
    ),

    # Customer Ticket Status
    path(
        "check-ticket-status/",
        views.check_ticket_status,
        name="check_ticket_status"
    ),

    # Admin Ticket Details and Status Update
    path(
        "ticket/<int:ticket_id>/",
        views.ticket_detail,
        name="ticket_detail"
    ),

    # Ticket Search, Status Filter and Pagination
    path(
        "manage-tickets/",
        views.manage_tickets,
        name="manage_tickets"
    ),

    # Customer Order Tracking
    path(
        "track-order/",
        views.track_order,
        name="track_order"
    ),

    # Admin Add New Order
    path(
        "add-order/",
        views.add_order,
        name="add_order"
    ),

    # Admin Order Management
    path(
        "manage-orders/",
        views.manage_orders,
        name="manage_orders"
    ),

]