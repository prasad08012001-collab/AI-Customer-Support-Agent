
from django.db import models


# Customer Conversation Model
class Conversation(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


# Chat Message Model
class ChatMessage(models.Model):

    MESSAGE_TYPES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session_key = models.CharField(
        max_length=40,
        blank=True,
        default="",
        db_index=True
    )

    message = models.TextField()

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default="user"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]


# Customer Support Ticket Model
class Ticket(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    subject = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


# Customer Order Model
class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("Placed", "Placed"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    order_id = models.CharField(
        max_length=20,
        unique=True
    )

    customer_name = models.CharField(max_length=100)

    customer_email = models.EmailField()

    product_name = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="Placed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_id
