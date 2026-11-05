# AI Customer Support Agent

An AI-powered customer support system built using **Python, Django, Django REST Framework, and Ollama**.

The application helps customers get AI-generated responses, create support tickets, verify ticket status, and track orders.

## Features

### 1. AI Chatbot
- AI-powered customer conversations using Ollama.
- Uses the `qwen2.5:3b` local language model.
- Maintains chat history.
- Handles normal customer queries.

### 2. Support Ticket Management
- Create support tickets.
- Collect customer name, email, subject, and description.
- Generate ticket IDs.
- Verify tickets using ticket ID and registered email.
- View and update ticket status.

### 3. Order Management
- Add new customer orders.
- Generate unique order IDs.
- Search and filter orders.
- Update order status.
- Track orders using order ID and email.
- Display order progress.

### 4. Admin Dashboard
- View dashboard statistics.
- Manage customer tickets.
- Manage customer orders.
- View customer chat history.

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- Ollama
- Qwen 2.5 (3B)
- HTML
- CSS
- JavaScript

## Project Structure

```text
AI_Customer_Support_Agent/
│
├── accounts/
├── chatbot/
├── config/
├── support/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/prasad08012001-collab/AI-Customer-Support-Agent.git
```

### 2. Open the project folder

```bash
cd AI-Customer-Support-Agent
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment (Windows)

```powershell
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Install and start Ollama

Install Ollama from:

https://ollama.com/download

Download the model:

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running locally.

### 7. Apply database migrations

```bash
python manage.py migrate
```

### 8. Start the Django server

```bash
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

## Security Notes

- Do not upload `.env` files or API keys.
- Do not upload your local virtual environment.
- Keep your local database out of public repositories.
- Use environment variables for sensitive configuration.

## Author

**Prasad Kimidi**

GitHub: https://github.com/prasad08012001-collab

## License

This project is currently provided for learning and demonstration purposes.