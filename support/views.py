import re
from uuid import uuid4
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Max, Q
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError


from .models import Conversation, ChatMessage, Ticket, Order
from chatbot.ai_service import generate_ai_response


# -----------------------------------------
# REGEX PATTERNS
# -----------------------------------------

EMAIL_PATTERN = (
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

ORDER_ID_PATTERN = r"\bORD(?=[A-Z0-9]*\d)[A-Z0-9]{4,}\b"


# -----------------------------------------
# SESSION FLOW HELPERS
# -----------------------------------------

def clear_pending_flows(request):

    flow_keys = [
        "ticket_draft",
        "waiting_for_ticket_id",
        "pending_ticket_status_id",
        "waiting_for_order_id",
        "pending_order_id",
    ]

    for key in flow_keys:
        request.session.pop(key, None)


# -----------------------------------------
# CUSTOMER DASHBOARD
# -----------------------------------------
@staff_member_required
def dashboard(request):

    total_conversations = Conversation.objects.count()

    resolved_conversations = Conversation.objects.filter(
        status="Resolved"
    ).count()

    pending_conversations = Conversation.objects.filter(
        status="Pending"
    ).count()

    success_rate = (
        round((resolved_conversations / total_conversations) * 100)
        if total_conversations else 0
    )

    recent_conversations = Conversation.objects.order_by(
        "-created_at"
    )[:5]

    total_messages = ChatMessage.objects.count()

    total_chat_sessions = (
        ChatMessage.objects
        .exclude(session_key="")
        .values("session_key")
        .distinct()
        .count()
    )

    recent_customer_chats = (
        ChatMessage.objects
        .exclude(session_key="")
        .values("session_key")
        .annotate(
            total_messages=Count("id"),
            last_message_time=Max("created_at")
        )
        .order_by("-last_message_time")[:5]
    )

    total_tickets = Ticket.objects.count()

    pending_tickets = Ticket.objects.filter(
        status="Pending"
    ).count()

    in_progress_tickets = Ticket.objects.filter(
        status="In Progress"
    ).count()

    resolved_tickets = Ticket.objects.filter(
        status="Resolved"
    ).count()

    recent_tickets = Ticket.objects.order_by(
        "-created_at"
    )[:5]

    total_orders = Order.objects.count()

    context = {
        "total_conversations": total_conversations,
        "resolved_conversations": resolved_conversations,
        "pending_conversations": pending_conversations,
        "success_rate": success_rate,
        "recent_conversations": recent_conversations,

        "total_chat_sessions": total_chat_sessions,
        "total_messages": total_messages,
        "recent_customer_chats": recent_customer_chats,

        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "recent_tickets": recent_tickets,

        "total_orders": total_orders,
    }

    return render(request, "dashboard.html", context)


# -----------------------------------------
# CUSTOMER CHAT
# -----------------------------------------

def chat(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.method == "POST":

        message = request.POST.get("message", "").strip()

        if not message:

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "error": "Please enter a message."
                }, status=400)

            return redirect("chat")

        # Save user message
        ChatMessage.objects.create(
            session_key=session_key,
            message=message,
            message_type="user"
        )

        lower_message = message.lower()

        # None means normal AI response is required.
        ai_reply = None

        # ---------------------------------
        # 1. IDENTIFY NEW REQUEST TYPES
        # ---------------------------------

        ticket_status_keywords = [
            "check my ticket",
            "check ticket",
            "ticket status",
            "track my ticket",
            "track ticket",
            "check my ticket status",
        ]

        ticket_keywords = [
            "create a support ticket",
            "create support ticket",
            "create ticket",
            "raise a ticket",
            "raise ticket",
            "open a ticket",
            "submit a complaint",
            "create complaint",
            "i want to create a ticket",
            "i want to create a support ticket",
        ]

        order_tracking_keywords = [
            "track my order",
            "track order",
            "order status",
            "check my order",
            "check order",
            "where is my order",
            "i want to track my order",
        ]

        is_ticket_status_request = any(
            keyword in lower_message
            for keyword in ticket_status_keywords
        )

        is_ticket_create_request = any(
            keyword in lower_message
            for keyword in ticket_keywords
        )

        is_order_tracking_request = any(
            keyword in lower_message
            for keyword in order_tracking_keywords
        )

        # ---------------------------------
        # 2. HANDLE NEW REQUESTS FIRST
        # ---------------------------------

        if (
            is_ticket_status_request
            or is_ticket_create_request
            or is_order_tracking_request
        ):

            clear_pending_flows(request)

            # Ticket status request
            if is_ticket_status_request:

                ticket_id_match = re.search(
                    r"\b(?:ticket\s*(?:id)?\s*#?\s*)(\d+)\b",
                    message,
                    re.IGNORECASE
                )

                if ticket_id_match:

                    ticket_id = ticket_id_match.group(1)

                    if Ticket.objects.filter(id=ticket_id).exists():

                        request.session[
                            "pending_ticket_status_id"
                        ] = ticket_id

                        ai_reply = (
                            f"I found Ticket ID {ticket_id}. "
                            "Please enter your registered email address."
                        )

                    else:

                        ai_reply = (
                            "Ticket ID not found. Please check your Ticket ID."
                        )

                else:

                    request.session["waiting_for_ticket_id"] = True

                    ai_reply = "Please enter your Ticket ID."

            # Ticket creation request
            elif is_ticket_create_request:

                request.session["ticket_draft"] = {
                    "step": "name"
                }

                ai_reply = (
                    "Sure! I can help you create a support ticket.\n"
                    "First, please enter your full name."
                )

            # Order tracking request
            elif is_order_tracking_request:

                order_match = re.search(
                    ORDER_ID_PATTERN,
                    message,
                    re.IGNORECASE
                )

                if order_match:

                    order_id = order_match.group(0).upper()

                    if Order.objects.filter(
                        order_id__iexact=order_id
                    ).exists():

                        request.session["pending_order_id"] = order_id

                        ai_reply = (
                            f"I found your order with ID {order_id}. "
                            "Please enter your registered email address."
                        )

                    else:

                        ai_reply = (
                            f"Order ID {order_id} not found. "
                            "Please check your Order ID."
                        )

                else:

                    request.session["waiting_for_order_id"] = True

                    ai_reply = (
                        "Sure! I can help you track your order.\n"
                        "Please enter your Order ID."
                    )

        # ---------------------------------
        # 3. TICKET CREATION FLOW
        # ---------------------------------

        elif request.session.get("ticket_draft"):

            ticket_draft = request.session["ticket_draft"]

            step = ticket_draft.get("step")

            if step == "name":

                if len(message) < 2:

                    ai_reply = "Please enter a valid full name."

                else:

                    ticket_draft["customer_name"] = message
                    ticket_draft["step"] = "email"

                    ai_reply = "Please enter your email address."

            elif step == "email":

                try:

                    validate_email(message)

                    ticket_draft["customer_email"] = message
                    ticket_draft["step"] = "subject"

                    ai_reply = "Please enter a subject for your problem."

                except ValidationError:

                    ai_reply = "Please enter a valid email address."

            elif step == "subject":

                if len(message) < 3:

                    ai_reply = "Please enter a meaningful subject."

                else:

                    ticket_draft["subject"] = message
                    ticket_draft["step"] = "description"

                    ai_reply = "Please describe your problem in detail."

            elif step == "description":

                if len(message) < 5:

                    ai_reply = (
                        "Please provide more details about your problem."
                    )

                else:

                    ticket = Ticket.objects.create(
                        customer_name=ticket_draft["customer_name"],
                        customer_email=ticket_draft["customer_email"],
                        subject=ticket_draft["subject"],
                        description=message,
                        status="Pending"
                    )

                    ai_reply = (
                        "Your support ticket has been created successfully!\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Subject: {ticket.subject}\n"
                        f"Status: {ticket.status}\n"
                        "You can use this Ticket ID to check your ticket status."
                    )

                    request.session.pop("ticket_draft", None)

            if request.session.get("ticket_draft"):

                request.session["ticket_draft"] = ticket_draft

        # ---------------------------------
        # 4. WAITING FOR TICKET ID
        # ---------------------------------

        elif request.session.get("waiting_for_ticket_id"):

            ticket_id_match = re.search(
                r"\b\d+\b",
                message
            )

            if ticket_id_match:

                ticket_id = ticket_id_match.group(0)

                if Ticket.objects.filter(id=ticket_id).exists():

                    request.session.pop(
                        "waiting_for_ticket_id",
                        None
                    )

                    request.session[
                        "pending_ticket_status_id"
                    ] = ticket_id

                    ai_reply = (
                        f"I found Ticket ID {ticket_id}. "
                        "Please enter your registered email address."
                    )

                else:

                    ai_reply = (
                        "Ticket ID not found. Please check the ID and try again."
                    )

            else:

                # Cancel old flow and allow normal AI chat.
                request.session.pop(
                    "waiting_for_ticket_id",
                    None
                )

        # ---------------------------------
        # 5. TICKET EMAIL VERIFICATION
        # ---------------------------------

        elif request.session.get("pending_ticket_status_id"):

            ticket_id = request.session.get(
                "pending_ticket_status_id"
            )

            email_match = re.search(
                EMAIL_PATTERN,
                message
            )

            if email_match:

                customer_email = email_match.group(0)

                try:

                    ticket = Ticket.objects.get(
                        id=ticket_id,
                        customer_email__iexact=customer_email
                    )

                    ai_reply = (
                        "Your ticket details:\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Customer: {ticket.customer_name}\n"
                        f"Subject: {ticket.subject}\n"
                        f"Description: {ticket.description}\n"
                        f"Current Status: {ticket.status}"
                    )

                except Ticket.DoesNotExist:

                    ai_reply = (
                        "We could not find a ticket matching "
                        "that Ticket ID and email address. "
                        "Please check your details."
                    )

                finally:

                    request.session.pop(
                        "pending_ticket_status_id",
                        None
                    )

            else:

                request.session.pop(
                    "pending_ticket_status_id",
                    None
                )

        # ---------------------------------
        # 6. WAITING FOR ORDER ID
        # ---------------------------------

        elif request.session.get("waiting_for_order_id"):

            entered_order_id = message.strip()

            order = None

            if entered_order_id.isdigit():

                order = Order.objects.filter(

                    id=int(entered_order_id)

                ).first()


            else:

                order = Order.objects.filter(

                    order_id__iexact=entered_order_id

                ).first()

            if order:

                request.session.pop(

                    "waiting_for_order_id",

                    None

                )

                request.session["pending_order_id"] = order.order_id

                ai_reply = (

                    f"I found your order with ID {order.order_id}. "

                    "Please enter your registered email address "

                    "to verify your order details."

                )


            else:

                ai_reply = (

                    f"Order ID {entered_order_id} not found. "

                    "Please check your Order ID and try again."

                )
        # ---------------------------------
        # 7. ORDER EMAIL VERIFICATION
        # ---------------------------------

        elif request.session.get("pending_order_id"):

            pending_order_id = request.session.get(
                "pending_order_id"
            )

            email_match = re.search(
                EMAIL_PATTERN,
                message
            )

            if email_match:

                customer_email = email_match.group(0).strip()

                try:

                    order = Order.objects.get(
                        order_id__iexact=pending_order_id,
                        customer_email__iexact=customer_email
                    )

                    ai_reply = (
                        "Your order details:\n"
                        f"Order ID: {order.order_id}\n"
                        f"Customer: {order.customer_name}\n"
                        f"Product: {order.product_name}\n"
                        f"Current Status: {order.status}"
                    )

                except Order.DoesNotExist:

                    ai_reply = (
                        "We could not find an order matching "
                        "that Order ID and email address. "
                        "Please check your registered email address."
                    )

                finally:

                    request.session.pop(
                        "pending_order_id",
                        None
                    )

            else:

                request.session.pop(
                    "pending_order_id",
                    None
                )

        # ---------------------------------
        # 8. DIRECT ORDER ID DETECTION
        # ---------------------------------

        if ai_reply is None:

            order_match = re.search(
                ORDER_ID_PATTERN,
                message,
                re.IGNORECASE
            )

            if order_match:

                order_id = order_match.group(0).upper()

                if Order.objects.filter(
                    order_id__iexact=order_id
                ).exists():

                    request.session["pending_order_id"] = order_id

                    ai_reply = (
                        f"I found your order with ID {order_id}. "
                        "Please enter your registered email address "
                        "to verify your order details."
                    )

                else:

                    ai_reply = (
                        f"Sorry, I could not find order {order_id}. "
                        "Please check your Order ID."
                    )

        # ---------------------------------
        # 9. NORMAL OLLAMA AI CHAT
        # ---------------------------------

        if ai_reply is None:

            previous_messages = ChatMessage.objects.filter(
                session_key=session_key
            ).order_by("created_at", "id")

            chat_history = []

            for msg in previous_messages:

                if msg.message_type in ["user", "assistant"]:

                    chat_history.append({
                        "role": msg.message_type,
                        "content": msg.message
                    })

            try:

                ai_reply = generate_ai_response(
                    message,
                    chat_history
                )

            except Exception as e:

                print("AI ERROR:", repr(e))

                ai_reply = (
                    "Sorry, our AI support service is temporarily "
                    "unavailable. Please try again later."
                )

        # ---------------------------------
        # 10. SAVE ASSISTANT RESPONSE
        # ---------------------------------

        ChatMessage.objects.create(
            session_key=session_key,
            message=ai_reply,
            message_type="assistant"
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":

            return JsonResponse({
                "user_message": message,
                "assistant_message": ai_reply,
            })

        return redirect("chat")

    messages = ChatMessage.objects.filter(
        session_key=session_key
    ).order_by("created_at", "id")

    return render(request, "chat.html", {
        "messages": messages
    })


# -----------------------------------------
# CLEAR CUSTOMER CHAT
# -----------------------------------------

@require_POST
def clear_chat(request):

    session_key = request.session.session_key

    if session_key:
        ChatMessage.objects.filter(
            session_key=session_key
        ).delete()

    clear_pending_flows(request)

    return redirect("chat")

# -----------------------------------------
# ALL CUSTOMER CHAT HISTORY
# -----------------------------------------

@staff_member_required
def chat_history(request):

    search_query = request.GET.get(
        "search", ""
    ).strip()

    customer_chats = (
        ChatMessage.objects
        .exclude(session_key="")
        .values("session_key")
        .annotate(
            total_messages=Count("id"),
            last_message_time=Max("created_at")
        )
    )

    if search_query:
        customer_chats = customer_chats.filter(
            session_key__icontains=search_query
        )

    customer_chats = customer_chats.order_by(
        "-last_message_time"
    )

    return render(request, "chat_history.html", {
        "customer_chats": customer_chats,
        "search_query": search_query,
    })


# -----------------------------------------
# INDIVIDUAL CUSTOMER CHAT HISTORY
# -----------------------------------------

@staff_member_required
def customer_chat_history(request, session_key):

    messages = ChatMessage.objects.filter(
        session_key=session_key
    ).order_by("created_at", "id")

    return render(request, "customer_chat_detail.html", {
        "messages": messages,
        "session_key": session_key,
    })
# -----------------------------------------
# CREATE CUSTOMER SUPPORT TICKET
# -----------------------------------------

@require_http_methods(["GET", "POST"])
def create_ticket(request):

    success = False
    error = ""

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        customer_email = request.POST.get(
            "customer_email", ""
        ).strip()

        subject = request.POST.get(
            "subject", ""
        ).strip()

        description = request.POST.get(
            "description", ""
        ).strip()

        if not all([
            customer_name,
            customer_email,
            subject,
            description
        ]):
            error = "Please fill in all fields."

        elif len(customer_name) > 100:
            error = "Customer name must not exceed 100 characters."

        elif len(subject) > 200:
            error = "Subject must not exceed 200 characters."

        elif len(description) > 5000:
            error = "Description must not exceed 5000 characters."

        else:
            try:
                validate_email(customer_email)

                Ticket.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    subject=subject,
                    description=description,
                    status="Pending"
                )

                success = True

            except ValidationError:
                error = "Please enter a valid email address."

    return render(request, "create_ticket.html", {
        "success": success,
        "error": error
    })
# -----------------------------------------
# CUSTOMER TICKET STATUS TRACKING
# -----------------------------------------

def check_ticket_status(request):

    ticket = None
    error = ""

    if request.method == "POST":

        ticket_id = request.POST.get(
            "ticket_id", ""
        ).strip()

        customer_email = request.POST.get(
            "customer_email", ""
        ).strip()

        try:

            validate_email(customer_email)

            ticket = Ticket.objects.get(
                id=ticket_id,
                customer_email__iexact=customer_email
            )

        except (Ticket.DoesNotExist, ValueError, ValidationError):

            error = "Invalid Ticket ID or Email Address."

    return render(request, "check_ticket_status.html", {
        "ticket": ticket,
        "error": error
    })


# -----------------------------------------
# ADMIN TICKET DETAILS AND STATUS UPDATE
# -----------------------------------------

@staff_member_required
@require_POST
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    success = False
    error = ""

    if request.method == "POST":

        new_status = request.POST.get(
            "status", ""
        )

        valid_statuses = [
            choice[0] for choice in Ticket.STATUS_CHOICES
        ]

        if new_status in valid_statuses:

            ticket.status = new_status
            ticket.save()

            success = True

        else:

            error = "Please select a valid ticket status."

    return render(request, "ticket_detail.html", {
        "ticket": ticket,
        "success": success,
        "error": error,
    })


# -----------------------------------------
# TICKET SEARCH, STATUS FILTER AND PAGINATION
# -----------------------------------------

@staff_member_required
def manage_tickets(request):

    search_query = request.GET.get(
        "search", ""
    ).strip()

    status_filter = request.GET.get(
        "status", ""
    ).strip()

    tickets = Ticket.objects.all().order_by("-created_at")

    if search_query:

        search_filter = (
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(subject__icontains=search_query)
        )

        if search_query.isdigit():

            search_filter |= Q(id=int(search_query))

        tickets = tickets.filter(search_filter)

    valid_statuses = [
        choice[0] for choice in Ticket.STATUS_CHOICES
    ]

    if status_filter in valid_statuses:

        tickets = tickets.filter(status=status_filter)

    else:

        status_filter = ""

    paginator = Paginator(tickets, 10)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "tickets": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,

        "total_tickets": Ticket.objects.count(),

        "pending_tickets": Ticket.objects.filter(
            status="Pending"
        ).count(),

        "in_progress_tickets": Ticket.objects.filter(
            status="In Progress"
        ).count(),

        "resolved_tickets": Ticket.objects.filter(
            status="Resolved"
        ).count(),
    }

    return render(request, "manage_tickets.html", context)


# -----------------------------------------
# CUSTOMER ORDER TRACKING
# -----------------------------------------

@require_http_methods(["GET", "POST"])
def track_order(request):

    order = None
    error = ""

    if request.method == "POST":

        order_id = request.POST.get(
            "order_id", ""
        ).strip()

        customer_email = request.POST.get(
            "customer_email", ""
        ).strip()

        if not order_id or not customer_email:

            error = "Please enter both Order ID and Email Address."

        elif len(order_id) > 20:

            error = "Invalid Order ID or Email Address."

        elif len(customer_email) > 254:

            error = "Invalid Order ID or Email Address."

        else:

            try:

                validate_email(customer_email)

                order = Order.objects.get(
                    order_id__iexact=order_id,
                    customer_email__iexact=customer_email
                )

            except (Order.DoesNotExist, ValidationError):

                error = "Invalid Order ID or Email Address."

    return render(request, "order_tracking.html", {
        "order": order,
        "error": error
    })

# -----------------------------------------
# ADMIN ADD NEW ORDER
# -----------------------------------------

@staff_member_required
@require_http_methods(["GET", "POST"])
def add_order(request):

    success = False
    error = ""
    order = None

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        customer_email = request.POST.get(
            "customer_email", ""
        ).strip()

        product_name = request.POST.get(
            "product_name", ""
        ).strip()

        if not customer_name or not customer_email or not product_name:
            error = "Please fill in all fields."

        elif len(customer_name) > 100:
            error = "Customer name must not exceed 100 characters."

        elif len(product_name) > 200:
            error = "Product name must not exceed 200 characters."

        else:
            try:
                validate_email(customer_email)

                order_id = "ORD" + uuid4().hex[:10].upper()

                order = Order.objects.create(
                    order_id=order_id,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    product_name=product_name,
                    status="Placed"
                )

                success = True

            except ValidationError:
                error = "Please enter a valid email address."

            except IntegrityError:
                error = "Unable to generate a unique Order ID. Please try again."

    return render(request, "add_order.html", {
        "success": success,
        "error": error,
        "order": order,
    })

# -----------------------------------------
# ADMIN ORDER MANAGEMENT
# SEARCH, STATUS FILTER AND PAGINATION
# -----------------------------------------

@staff_member_required
@require_http_methods(["GET", "POST"])
def manage_orders(request):

    success = False
    error = ""

    if request.method == "POST":

        search_query = request.POST.get(
            "search", ""
        ).strip()

        status_filter = request.POST.get(
            "filter_status", ""
        ).strip()

        page_number = request.POST.get(
            "page", "1"
        )

    else:

        search_query = request.GET.get(
            "search", ""
        ).strip()

        status_filter = request.GET.get(
            "status", ""
        ).strip()

        page_number = request.GET.get(
            "page", "1"
        )

    valid_statuses = [
        choice[0] for choice in Order.ORDER_STATUS_CHOICES
    ]

    if status_filter not in valid_statuses:
        status_filter = ""

    # UPDATE ORDER STATUS

    if request.method == "POST" and "order_pk" in request.POST:

        order_pk = request.POST.get(
            "order_pk", ""
        )

        new_status = request.POST.get(
            "status", ""
        )

        if new_status not in valid_statuses:

            error = "Please select a valid order status."

        else:

            try:

                order = get_object_or_404(
                    Order,
                    id=order_pk
                )

                order.status = new_status

                order.save(
                    update_fields=["status", "updated_at"]
                )

                success = True

            except (ValueError, TypeError):

                error = "Invalid Order."

    # GET ALL ORDERS

    orders = Order.objects.all().order_by("-created_at")

    # SEARCH

    if search_query:

        search_filter = (
            Q(order_id__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )

        orders = orders.filter(search_filter)

    # STATUS FILTER

    if status_filter:

        orders = orders.filter(
            status=status_filter
        )

    # PAGINATION

    paginator = Paginator(orders, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "page_obj": page_obj,

        "search": search_query,
        "selected_status": status_filter,

        "status_choices": Order.ORDER_STATUS_CHOICES,

        "success": success,
        "error": error,
    }

    return render(request, "manage_orders.html", context)