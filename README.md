# WalletWise

![WalletWise](https://img.shields.io/badge/WalletWise-Personal%20Finance-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791?style=flat-square&logo=postgresql)

## Problem Statement

Managing personal finances is hard. Most people lack visibility into where their money goes, have no easy way to categorize spending, and receive no actionable guidance on how to improve. WalletWise solves this by providing a single dashboard to track income and expenses, visualize spending trends over time, and receive AI-powered financial advice — all with real-time updates and voice memo support for on-the-go transaction logging.

---

## Screenshots

> **TODO:** Replace the placeholders below with actual screenshots.

| Dashboard | Transactions | AI Insights |
|-----------|-------------|-------------|
| ![Dashboard screenshot](docs/screenshots/dashboard.png) | ![Transactions screenshot](docs/screenshots/transactions.png) | ![AI Insights screenshot](docs/screenshots/ai-insights.png) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│              React 19 + TypeScript (port 3000)              │
│         Tailwind CSS · Chart.js · React Router              │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST  +  WebSocket (Socket.IO)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask 3.0 API                          │
│                   Python (port 5000)                        │
│                                                             │
│  /api/auth      /api/transactions      /api/dashboard       │
│  /api/ai        /api/admin             WebSocket events     │
│                                                             │
│  Flask-JWT-Extended · Flask-SocketIO · Flask-CORS           │
└───────────┬─────────────────────────┬───────────────────────┘
            │                         │
            ▼                         ▼
┌───────────────────┐     ┌───────────────────────────────────┐
│   PostgreSQL DB   │     │         Gemini AI API             │
│  (SQLAlchemy ORM) │     │  (generativelanguage.googleapis)  │
└───────────────────┘     └───────────────────────────────────┘
```

**Key data flows:**
- The frontend communicates with the backend via REST for CRUD operations and a persistent Socket.IO connection for real-time dashboard updates.
- The backend uses SQLAlchemy to read/write from PostgreSQL and proxies AI requests to the Google Gemini API.
- Audio memos are stored as files on the backend server and referenced by path in the database.

---

## Local Dev Setup

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 16+ |
| Python | 3.8+ |
| PostgreSQL | 12+ |
| npm | 8+ |
| pip | latest |

### 1. Clone the repo

```bash
git clone https://github.com/Vivekanand-Yadav7/WalletWise.git
cd WalletWise
```

### 2. Database

```sql
CREATE DATABASE walletwise_dev;
-- If your user is not 'postgres', adjust accordingly
GRANT ALL PRIVILEGES ON DATABASE walletwise_dev TO postgres;
```

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=change-me-in-production

# JWT
JWT_SECRET_KEY=change-me-in-production

# Database (choose one)
DEV_DATABASE_URL=postgresql://postgres:your_password@localhost/walletwise_dev

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
# Optional — defaults to gemini-2.0-flash endpoint
# GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent

# Server
PORT=5000
```

Initialize the database and start the server:

```bash
python setup.py          # or: python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
python main.py
```

The API will be available at `http://localhost:5000`.

### 4. Frontend

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`.

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `development` | Flask environment (`development` / `production`) |
| `SECRET_KEY` | **Yes** | insecure default | Flask session secret |
| `JWT_SECRET_KEY` | **Yes** | insecure default | JWT signing secret |
| `DEV_DATABASE_URL` | **Yes** (dev) | — | PostgreSQL connection string for development |
| `PROD_DATABASE_URL` | **Yes** (prod) | — | PostgreSQL connection string for production |
| `GEMINI_API_KEY` | **Yes** | — | Google Gemini API key for AI insights |
| `GEMINI_API_URL` | No | Gemini 2.0 Flash endpoint | Override Gemini API endpoint |
| `PORT` | No | `5000` | Port the Flask server listens on |

---

## Deployment Notes

### Frontend

Build a production bundle and serve the static files via any web server (Nginx, Vercel, Netlify, S3+CloudFront, etc.):

```bash
cd frontend
npm run build          # outputs to frontend/build/
```

Set the `REACT_APP_API_URL` environment variable (or update `src/services/api.ts`) to point to your production backend URL before building.

### Backend

1. Set all required environment variables on the server (use `PROD_DATABASE_URL` instead of `DEV_DATABASE_URL`).
2. Run with a production WSGI server. Because WalletWise uses Socket.IO + eventlet, use:

```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:${PORT:-5000} main:app
```

> **Note:** Socket.IO requires a single worker when using eventlet. For horizontal scaling, configure a Redis adapter (`flask-socketio` supports this via `message_queue`).

3. Serve the `frontend/build/` static files either from the same server (e.g., Nginx reverse-proxy) or a CDN.

### Nginx Reverse-Proxy Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve React build
    location / {
        root /var/www/walletwise/frontend/build;
        try_files $uri /index.html;
    }

    # Proxy API & WebSocket to Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Creating an Admin User

```bash
cd backend
source venv/bin/activate
flask --app main create-admin
```

---

## Project Structure

```
WalletWise/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── config.py            # Config classes (dev / prod / test)
│   │   ├── socketio_events.py   # WebSocket event handlers
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── transaction.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── transaction.py
│   │   │   ├── admin.py
│   │   │   └── ai.py
│   │   └── utils/
│   │       └── auth_utils.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT tokens |
| GET | `/api/auth/profile` | Get current user profile |
| GET | `/api/transactions` | List transactions (paginated) |
| POST | `/api/transactions` | Create a transaction |
| PUT | `/api/transactions/:id` | Update a transaction |
| DELETE | `/api/transactions/:id` | Delete a transaction |
| GET | `/api/dashboard/summary` | Income / expense / balance totals |
| GET | `/api/dashboard/charts` | Chart data for analytics |
| POST | `/api/ai/analyze` | Get AI-powered spending analysis |
| POST | `/api/ai/advice` | Get personalized financial advice |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Tailwind CSS, Chart.js, React Router 7 |
| Backend | Flask 3.0, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-SocketIO |
| Database | PostgreSQL 12+ |
| AI | Google Gemini 2.0 Flash |
| Real-time | Socket.IO (eventlet) |

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request.

## License

MIT — see [LICENSE](LICENSE) for details.
