# CureLink: Modern AI Healthcare Assistant

CureLink is a high-performance, real-time consultation platform that uses AI to help doctors and patients stay connected. It features a WhatsApp-style chat interface, clinical-grade memory, and personalized AI guidance based on user health profiles.

## 📚 Project Documentation

We have split our documentation into three main areas to help you navigate the system:

### 1. [High-Level Design (HLD)](./backend/HLD.md)
*The "Why" and the Logic.*
Read this for the birds-eye view of our architecture, how data flows through the system, and our future roadmap for scaling to thousands of users.

### 2. [Low-Level Design (LLD)](./backend/LLD.md)
*The "How" and the Blueprint.*
Read this for the technical details: our database schemas, service-by-service breakdowns, folder structure, and the specific rules our code follows.

### 3. [Frontend Documentation](./frontend/README.md)
*The "Look" and the Experience.*
Read this for details on how we built the responsive UI, our theme system, and how we handle real-time WebSockets with "Protocol-Aware" logic.

---

## 🚀 Quick Start (Docker)

The fastest way to get CureLink running locally is using Docker Compose.

```bash
# Clone and enter the project
cd curelink

# Build and start all services
docker compose up --build -d
```

Once running, you can access:
- **Frontend**: [http://localhost](http://localhost)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, TailwindCSS, Framer Motion.
- **Backend**: FastAPI, SQLModel (PostgreSQL), Redis.
- **Inference**: OpenRouter (GPT/Claude) with structured clinical prompts.
- **Deployment**: Nginx, Docker.
