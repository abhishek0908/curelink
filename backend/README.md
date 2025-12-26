# CureLink Backend: The Clinical Intelligence

This is the core of CureLink. It handles the data, the security, and most importantly, the communication with our AI models. It's designed to be fast, reliable, and medically accurate.

## 🛠️ The Logic Behind the Scenes
Instead of one big mess, we’ve built the backend using a modular service-oriented approach. This means if we want to change how the AI summarizes a chat, we only have to update the `LLMService`, without touching our login or database code.

### 📚 Detailed Design Docs
If you really want to under the hood, we have two primary design guides:
- **[High-Level Design (HLD)](./HLD.md)**: This is our architectural vision—how data flows from a user's phone to the AI and back.
- **[Low-Level Design (LLD)](./LLD.md)**: This is the actual blueprint—database tables, folder structures, and specific coding patterns.

---

## 🚀 How to Run Locally (Manually)

While we recommend using the main [Docker Compose](../README.md) file, you can also run the backend manually for development.

### 1. Prerequisites
- Python 3.11+
- A running PostgreSQL and Redis instance.

### 2. Setup
```bash
# Create and enter a virtual environment
python -m venv venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 3. Database Migrations
We use Alembic to keep our database structure in sync:
```bash
alembic upgrade head
```

### 4. Start the Engine
```bash
uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`. You can explore the **Swagger UI** at `/docs` to test the endpoints directly.

---

## 🔑 Key Components
- **AuthService**: Handles secure logins using JWT tokens.
- **ChatService**: Manages the live conversation and ensures data is saved atomically.
- **MemoryService**: Keeps track of recent history and triggers clinical summaries.
- **LLMService**: Our AI's "Brain"—it builds the medically-focused prompts for GPT and Claude.
