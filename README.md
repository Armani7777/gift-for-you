# Date Invitation

A mobile-first web app for creating a personalized, interactive date invitation and sharing it with a unique private link.

## Stack

- Backend: Python, Django, Django REST Framework, PostgreSQL
- Frontend: Vue 3, Vite, TypeScript, Vue Router, Pinia

This project uses its **own** local PostgreSQL database: `date_invitation`.
Do not point it at databases from other projects.

## Local setup

### 1. Database

Create a dedicated local database (do not reuse other project databases):

```sql
CREATE DATABASE date_invitation;
```

Copy `backend/.env.example` to `backend/.env` and set local credentials.

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8010
```

API: `http://127.0.0.1:8010/api/`

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: `http://127.0.0.1:5174/`

## Routes

| Path | Purpose |
| --- | --- |
| `/` | Landing page |
| `/create` | Creator wizard |
| `/demo` | Static demo invitation |
| `/i/:token` | Public invitation |
| `/manage/:token/:managementToken` | Creator status page |
