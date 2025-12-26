# CureLink Backend

This is the backend service for CureLink, a health-focused AI assistant.

## Documentation
We maintain detailed design documentation for the system:

- **[High-Level Design (HLD)](./HLD.md)**: Architectural overview, tech stack, and system-wide workflows.
- **[Low-Level Design (LLD)](./LLD.md)**: Detailed folder structure, database schema, and service-layer patterns.

## Getting Started
### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL & Redis

### Local Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
Once the server is running, you can access the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
