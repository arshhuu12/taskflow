<div align="center">

# ✦ TaskFlow

**A production-ready Task Management System built with FastAPI + Vanilla JS**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)](https://sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Features](#-features) · [Architecture](#-architecture) · [API Docs](#-api-documentation) · [Run Locally](#-run-locally) · [Deploy](#-deployment)

</div>

---

## 📌 Overview

**TaskFlow** is a full-stack task management application that lets you create, prioritise, filter, and track tasks through their lifecycle — from *To Do* to *Done*.

- **Backend** — REST API built with FastAPI, SQLAlchemy ORM, and Pydantic v2
- **Frontend** — Responsive SPA written in pure HTML / CSS / Vanilla JS (no build step)
- **Database** — SQLite in development; PostgreSQL in production (Render)
- **Deployment** — Render (backend), GitHub Pages or Render Static (frontend)

---

## ✨ Features

| Category | Details |
|---|---|
| **Task CRUD** | Create, view, edit, and delete tasks |
| **Status Tracking** | `todo` → `in_progress` → `done` lifecycle |
| **Priority Levels** | High 🔴 / Medium 🟡 / Low 🟢 |
| **Due Dates** | Set deadlines; overdue tasks are highlighted |
| **Filters** | Filter by status pill and/or priority dropdown |
| **Mark Complete** | One-click endpoint sets `is_completed = true` and `status = done` |
| **Timestamps** | `created_at` and `updated_at` managed automatically |
| **CORS** | Configurable allowed-origins for frontend ↔ backend separation |
| **API Docs** | Auto-generated Swagger UI at `/docs` and ReDoc at `/redoc` |
| **Toast Alerts** | Non-blocking success / error / info notifications |
| **Delete Modal** | Confirmation dialog before permanent deletion |
| **Loading State** | Spinner shown while API calls are in-flight |
| **Responsive UI** | Two-column desktop layout collapses to single column on mobile |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
│                                                                  │
│   ┌──────────────┐   fetch()   ┌──────────────────────────────┐ │
│   │  index.html  │ ──────────► │         app.js               │ │
│   │  (SPA shell) │             │  CONFIG · State · Render      │ │
│   └──────────────┘             │  API helpers · Event handlers │ │
│   ┌──────────────┐             └────────────┬─────────────────┘ │
│   │  styles.css  │                          │  HTTP / JSON       │
│   │ (design sys) │                          │                    │
│   └──────────────┘                          ▼                    │
└─────────────────────────────────────────────┼────────────────────┘
                                              │
                              CORS middleware │
                                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND  (FastAPI / uvicorn)                 │
│                                                                  │
│   main.py                                                        │
│   ├── CORSMiddleware                                             │
│   ├── Lifespan → Base.metadata.create_all()                      │
│   └── include_router(task_router)                                │
│                                                                  │
│   routers/task_router.py                                         │
│   ├── POST   /tasks/                                             │
│   ├── GET    /tasks/          ← ?status= &priority= filters      │
│   ├── GET    /tasks/{id}                                         │
│   ├── PUT    /tasks/{id}                                         │
│   ├── PATCH  /tasks/{id}/complete                                │
│   └── DELETE /tasks/{id}                                         │
│                                                                  │
│   models/task.py   ← SQLAlchemy ORM                             │
│   schemas/         ← Pydantic v2 (TaskCreate / TaskOut / …)     │
│   utils/response.py← Standardised JSON envelope                 │
│   config.py        ← Pydantic BaseSettings (env vars)           │
│   database.py      ← engine, SessionLocal, get_db()             │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │  SQLAlchemy ORM
                           ▼
              ┌────────────────────────┐
              │      DATABASE          │
              │  SQLite  (dev)         │
              │  PostgreSQL  (prod)    │
              └────────────────────────┘
```

---

## 🗂 Project Structure

```
taskflow/
│
├── backend/
│   ├── main.py                  # App entry point, CORS, lifespan
│   ├── database.py              # Engine, SessionLocal, Base, get_db
│   ├── config.py                # Pydantic Settings (env vars)
│   ├── requirements.txt         # All Python dependencies
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Task ORM model + enums
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task_schema.py       # TaskCreate, TaskUpdate, TaskOut, TaskComplete
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── task_router.py       # All CRUD endpoints
│   │
│   └── utils/
│       ├── __init__.py
│       └── response.py          # success_response, error_response, not_found
│
├── frontend/
│   ├── index.html               # SPA shell
│   ├── styles.css               # Full design system (CSS custom properties)
│   └── app.js                   # CRUD logic, rendering, event handling
│
└── README.md
```

---

## 🗃 ERD Diagram

```
┌────────────────────────────────────────────────────┐
│                       tasks                        │
├──────────────┬──────────────────────────┬──────────┤
│  Column      │  Type                    │  Notes   │
├──────────────┼──────────────────────────┼──────────┤
│  id          │  INTEGER                 │  PK, AI  │
│  title       │  VARCHAR(255)            │  NOT NULL│
│  description │  TEXT                    │  nullable│
│  status      │  ENUM(todo,              │  default │
│              │    in_progress, done)    │   'todo' │
│  priority    │  ENUM(low,medium,high)   │  default │
│              │                          │ 'medium' │
│  is_completed│  BOOLEAN                 │  default │
│              │                          │   false  │
│  due_date    │  DATETIME (tz-aware)     │  nullable│
│  created_at  │  DATETIME (tz-aware)     │  auto    │
│  updated_at  │  DATETIME (tz-aware)     │  auto    │
└──────────────┴──────────────────────────┴──────────┘

              (single-table MVP; future tables
               could add Users, Tags, Comments)
```

---

## 📡 API Documentation

### Base URL

| Environment | URL |
|---|---|
| Development | `http://localhost:8000` |
| Production  | `https://your-taskflow-api.onrender.com` |

Interactive docs → `/docs` (Swagger) · `/redoc` (ReDoc)

---

### Response Envelope

Every endpoint returns a consistent shape:

```json
{
  "success": true,
  "message": "Human-readable summary.",
  "data": { }
}
```

Errors use FastAPI's native `HTTPException`:
```json
{ "detail": "Task not found." }
```

---

### `POST /tasks/` — Create a task

**Request body**

```json
{
  "title": "Deploy to production",
  "description": "Push the Docker image and migrate the DB.",
  "priority": "high",
  "due_date": "2025-12-31T23:59:00Z"
}
```

**Response `201 Created`**

```json
{
  "success": true,
  "message": "Task created successfully.",
  "data": {
    "id": 1,
    "title": "Deploy to production",
    "description": "Push the Docker image and migrate the DB.",
    "status": "todo",
    "priority": "high",
    "is_completed": false,
    "due_date": "2025-12-31T23:59:00Z",
    "created_at": "2025-02-24T10:30:00Z",
    "updated_at": "2025-02-24T10:30:00Z"
  }
}
```

---

### `GET /tasks/` — List tasks

| Query param | Type | Options | Default |
|---|---|---|---|
| `status` | string | `todo` · `in_progress` · `done` | all |
| `priority` | string | `low` · `medium` · `high` | all |
| `skip` | integer | ≥ 0 | 0 |
| `limit` | integer | 1–500 | 100 |

```bash
# All tasks
GET /tasks/

# Filtered
GET /tasks/?status=todo&priority=high&skip=0&limit=20
```

**Response `200 OK`**

```json
{
  "success": true,
  "message": "3 task(s) found.",
  "data": {
    "total": 3,
    "skip": 0,
    "limit": 100,
    "tasks": [ { "id": 1, "..." : "..." } ]
  }
}
```

---

### `GET /tasks/{id}` — Get a task

```bash
GET /tasks/1
```

Returns the full `TaskOut` object or `404` if not found.

---

### `PUT /tasks/{id}` — Update a task

All fields are optional — only supplied fields are written.

```json
{
  "title": "Deploy to production (v2)",
  "status": "in_progress",
  "priority": "medium"
}
```

**Response `200 OK`** — returns the updated `TaskOut`.

---

### `PATCH /tasks/{id}/complete` — Mark as completed

No request body needed.

**Response `200 OK`**

```json
{
  "success": true,
  "message": "Task marked as completed.",
  "data": {
    "id": 1,
    "is_completed": true,
    "status": "done",
    "updated_at": "2025-02-24T11:00:00Z"
  }
}
```

---

### `DELETE /tasks/{id}` — Delete a task

**Response `200 OK`**

```json
{
  "success": true,
  "message": "Task 1 deleted successfully.",
  "data": { "deleted_id": 1 }
}
```

---

## 🚀 Run Locally

### Prerequisites

- Python 3.11+
- A modern browser (Chrome, Firefox, Edge)

### 1 — Clone the repo

```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow
```

### 2 — Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# (Optional) copy env template
cp .env.example .env           # edit DATABASE_URL, ALLOWED_ORIGINS, etc.

# Run development server
uvicorn main:app --reload
```

> The SQLite database file `taskflow.db` is auto-created in `backend/` on first run.
>
> - API root → http://localhost:8000  
> - Swagger UI → http://localhost:8000/docs

### 3 — Frontend

```bash
# From the project root — serve the frontend folder
python -m http.server 5500 --directory frontend

# OR just open frontend/index.html directly in your browser
```

> Open **http://localhost:5500** — the app connects to the local API automatically.

---

## ⚙️ Environment Variables

Create a `.env` file inside `backend/`:

```env
# Database
DATABASE_URL=sqlite:///./taskflow.db

# App
APP_ENV=development
DEBUG=true

# CORS — comma-separated origins allowed to call the API
ALLOWED_ORIGINS=["http://localhost:5500","http://127.0.0.1:5500"]
```

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./taskflow.db` | Database connection string |
| `APP_ENV` | `development` | `development` or `production` |
| `DEBUG` | `true` | Enable SQL echo and FastAPI debug mode |
| `ALLOWED_ORIGINS` | see above | JSON list of CORS-allowed origins |

---

## 🔄 Switching SQLite → PostgreSQL

1. Provision a PostgreSQL database (Render, Supabase, Neon, etc.)
2. Copy the connection string, e.g.:
   ```
   postgresql://user:password@host:5432/taskflow_db
   ```
3. Set it as an environment variable:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/taskflow_db
   ```
4. `psycopg2-binary` is already in `requirements.txt` — no code changes needed.
5. Restart the server; `create_all()` will create the tables in PostgreSQL automatically.

> **For production migrations**, use [Alembic](https://alembic.sqlalchemy.org) instead of `create_all()`:
> ```bash
> alembic init alembic
> alembic revision --autogenerate -m "initial"
> alembic upgrade head
> ```

---

## 🌐 Deployment

### Backend → Render Web Service

1. Push the repo to GitHub.
2. On [Render](https://render.com) → **New → Web Service** → connect your repo.
3. Set **Root Directory** to `backend`.
4. Configure:

   | Setting | Value |
   |---|---|
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. Add **Environment Variables** in the Render dashboard:

   ```
   DATABASE_URL   = postgresql://user:pass@host:5432/taskflow_db
   APP_ENV        = production
   DEBUG          = false
   ALLOWED_ORIGINS= ["https://your-frontend.com"]
   ```

### Database → Render PostgreSQL

1. On Render → **New → PostgreSQL**.
2. Copy the **Internal Database URL**.
3. Paste it as `DATABASE_URL` in your Web Service environment variables.

### Frontend → GitHub Pages

1. Push your `frontend/` folder to a `gh-pages` branch:
   ```bash
   git subtree push --prefix frontend origin gh-pages
   ```
2. Enable GitHub Pages in repo **Settings → Pages → Branch: gh-pages**.

### Frontend → Render Static Site

1. On Render → **New → Static Site** → connect your repo.
2. Set **Publish Directory** to `frontend`.
3. No build command needed.

### After deploying both

Edit `frontend/app.js` line 1:

```js
// Comment out dev, uncomment prod:
// BASE_URL: "http://localhost:8000",
BASE_URL: "https://your-taskflow-api.onrender.com",
```

---

## 🖼 Screenshots

> _Replace these placeholders with actual screenshots once the app is running._

| View | Screenshot |
|---|---|
| **Task Board** | ![Task Board](screenshots/task-board.png) |
| **Add Task Form** | ![Add Task](screenshots/add-task.png) |
| **Filter Bar** | ![Filters](screenshots/filters.png) |
| **Swagger UI** | ![API Docs](screenshots/swagger.png) |

---

## 🛣 Future Improvements

- [ ] **User Authentication** — JWT-based login with `python-jose` / OAuth2
- [ ] **User-Task ownership** — tasks belong to a user, not globally shared
- [ ] **Tags / Labels** — many-to-many relationship between tasks and tags
- [ ] **Subtasks** — nested task hierarchy (self-referential FK)
- [ ] **Comments** — per-task comment thread
- [ ] **Drag-and-drop Kanban** — visual board using the HTML Drag-and-Drop API
- [ ] **Dark mode** — CSS media query `prefers-color-scheme: dark`
- [ ] **Alembic migrations** — replace `create_all()` for safe schema evolution
- [ ] **Rate limiting** — `slowapi` middleware to protect public endpoints
- [ ] **WebSockets** — real-time task updates pushed from server to all clients
- [ ] **Unit & integration tests** — `pytest` + `httpx.AsyncClient`
- [ ] **Docker** — `Dockerfile` + `docker-compose.yml` for one-command local setup

---

## 🧰 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | 0.111 |
| ASGI Server | Uvicorn | 0.29 |
| ORM | SQLAlchemy | 2.0 |
| Migrations | Alembic | 1.13 |
| Validation | Pydantic v2 | 2.7 |
| Config | pydantic-settings | 2.2 |
| DB (dev) | SQLite | built-in |
| DB (prod) | PostgreSQL | 15+ |
| PG Driver | psycopg2-binary | 2.9 |
| Frontend | HTML5 / CSS3 / Vanilla JS (ES Modules) | — |
| Fonts | Inter (Google Fonts) | — |
| Hosting | Render | — |

---

## 👤 Author

**Your Name**  
Full-Stack Developer

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- Email: you@example.com

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ♥ using FastAPI + Vanilla JS

⭐ Star this repo if you found it useful!

</div>
