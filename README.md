 
# AI Customer Support Agent

An AI-powered customer support system built using **Python, Django, Django REST Framework, and Ollama**. It helps customers get instant responses, create support tickets, verify ticket status, and track orders.

## Features

### 1. AI Chatbot
- AI-powered customer conversations using Ollama.
- Uses the `qwen2.5:3b` local language model.
- Maintains chat history.
- Handles normal customer queries.

### 2. Support Ticket Management
- Create support tickets through the chatbot.
- Collect customer name, email, subject, and problem description.
- Generate ticket IDs.
- Verify tickets using Ticket ID and registered email.
- View and update ticket status.
- Search and filter tickets.

### 3. Order Management
- Add new customer orders.
- Generate unique order IDs.
- Track orders using Order ID and registered email.
- Update order status:
  - Placed
  - Processing
  - Shipped
  - Delivered
  - Cancelled
- Search and filter orders.

### 4. Admin Dashboard
- View ticket statistics.
- View recent conversations.
- Manage support tickets.
- Manage customer orders.
- Update ticket and order statuses.

### 5. REST API
- User registration and login.
- Token-based authentication.
- Authenticated chatbot API.
- Chat history retrieval.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| Django REST Framework | REST API development |
| Ollama | Local AI model integration |
| Qwen 2.5 (3B) | Language model |
| SQLite | Database |
| HTML | Web page structure |
| CSS | Styling |
| JavaScript | Frontend interactions |
| Postman | API testing |
| PyCharm | Development environment |

## Project Structure

```text
AI_Customer_Support_Agent/
│
├── accounts/
├── chatbot/
│   ├── ai_service.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── support/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── admin.py
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── manage.py
├── db.sqlite3
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI_Customer_Support_Agent
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install django djangorestframework
```

Install any additional packages used by the project.

### 4. Install and Start Ollama

Install Ollama from:

https://ollama.com/

Download the model:

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running locally.

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin Account

```bash
python manage.py createsuperuser
```

### 7. Start Django Server

```bash
python manage.py runserver
```

Open:

http://127.0.0.1:8000/

## Application URLs

| Page | URL |
|---|---|
| Dashboard | `/dashboard/` |
| Chatbot | `/chat/` |
| Create Ticket | `/create-ticket/` |
| Check Ticket Status | `/check-ticket-status/` |
| Manage Tickets | `/manage-tickets/` |
| Track Order | `/track-order/` |
| Add Order | `/add-order/` |
| Manage Orders | `/manage-orders/` |
| Django Admin | `/admin/` |

## API Endpoints

The project includes registration, login, and authenticated chatbot APIs.

The chatbot API uses token-based authentication. Send the authentication token in the request header when accessing protected endpoints.

Example:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

## Testing

The following features have been manually tested:

- AI chatbot responses using Ollama.
- Normal chat during an order-tracking conversation.
- Order ID and email verification.
- Ticket creation.
- Ticket status verification.
- Ticket status updates.
- Order creation.
- Order status updates.
- Order search and filtering.
- Customer order tracking.
- Admin dashboard statistics.

## Future Improvements

- Add automated tests.
- Improve chatbot intent detection.
- Add more customer support integrations.
- Deploy the application to a cloud server.
- Add role-based access control.

## Author

**Prasad**

## License

This project is developed for educational and portfolio purposes.
