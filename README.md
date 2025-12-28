# CureLink: Modern AI Healthcare Assistant

---

## 📚 Explore the Documentation

To keep things organized, we've broken down our documentation into three core sections. Whether you're interested in the business logic, the technical blueprint, or the user experience, you'll find it here:

### 🧠 [Backend Service: Logic & Intelligence](./backend/README.md)
This is where the "heavy lifting" happens. It contains everything about our FastAPI server, database , and the AI logic that powers our consultant, **Disha**.
- **Special Guides**: [High-Level Design (HLD)](./backend/HLD.md) | [Low-Level Design (LLD)](./backend/LLD.md)

### 🎨 [Frontend App: The User Experience](./frontend/README.md)
Explore how we built our sleek, "WhatsApp-style" chat interface. This README covers our theme system, responsive mobile layouts, and how we handle real-time WebSockets.

---

## 🚀 Getting Started (Fast)

We’ve dockerized the entire setup so you can get a production-ready environment running in seconds.

### 1. Prerequisites
- Docker & Docker Compose installed.
- An API Key from **OpenRouter** (to power the AI).

### 2. Setup Environment
Before launching, you need to configure your credentials:
```bash
# Copy the example file to production
cp backend/.env.example backend/.env.production
```
Open `backend/.env.production` and fill in your `OPENROUTER_API_KEY`. (You can also adjust your database and Redis settings here).

### 3. Launch with Docker
```bash
# Build and start everything in the background
docker compose up --build -d
```

### 4. Access the App
- **The Chat Interface**: [http://localhost](http://localhost)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ The Technology Behind CureLink

- **Fast & Reliable**: Built with **FastAPI** (Python 3.11) and **React** (TypeScript).
- **Clinical Memory**: Uses **PostgreSQL** for permanent records and **Redis** for lightning-fast conversation context.
- **Smart Conversations**: Integrated with **OpenRouter**, allowing us to use the world's most advanced AI models (GPT-4/Claude) with clinical guardrails.
- **Production-Ready**: Served behind an **Nginx** reverse proxy and fully containerized with **Docker**.
