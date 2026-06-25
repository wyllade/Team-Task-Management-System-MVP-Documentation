# Team Task Management System MVP

A beginner-friendly Jira-like task management app built with Flask + React.

Teams can create projects, assign tasks, track progress through a Kanban board, and discuss work through comments.

## Tech Stack

- **Backend**: Flask, Flask-CORS, PyJWT
- **Frontend**: React 18, React Router, Vite
- **Storage**: In-memory (resets on server restart; swap to SQLite/PostgreSQL for production)

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs at `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App opens at `http://localhost:5173`.

### Demo Account

- **Email**: `demo@test.com`
- **Password**: `pass`

## Features

- **Auth** — Register, login, JWT-protected routes
- **Projects** — Create, edit, delete (admin only), inline rename
- **Members** — Add/remove members per project, admin/member roles
- **Kanban Board** — 4 columns (Todo, In Progress, Review, Done), move tasks with one click
- **Tasks** — Create with title, description, priority (Low/Medium/High/Critical), assign to members
- **Task Details** — Dedicated page per task with status badge, priority, assignee, creator, and comments
- **Comments** — Add comments on any task, displayed with username
- **Dashboard** — Stats cards (projects, tasks, completed), project list with member counts
- **Logout** — Clears token, redirects to login

## Project Structure

```
backend/
  app.py              Flask API (all routes, auth, helpers)
  requirements.txt
frontend/
  src/
    App.jsx           Router setup (/, /dashboard, /project/:id, /task/:id)
    Login.jsx         Login + Register form
    Dashboard.jsx     Project list, stats, create/edit/delete
    ProjectPage.jsx   Kanban board, task CRUD, member management, comments
    TaskPage.jsx      Single task detail with comments and status change
    App.css           All styles
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | /register | Create account, returns JWT |
| POST | /login | Login, returns JWT |
| GET | /users | List all users |
| GET | /projects | List user's projects |
| POST | /projects | Create project |
| PUT | /projects/:id | Edit project (admin) |
| DELETE | /projects/:id | Delete project (admin) |
| GET | /projects/:id/members | List project members |
| POST | /projects/:id/members | Add member (admin) |
| DELETE | /projects/:id/members/:uid | Remove member (admin) |
| GET | /tasks?project_id= | List tasks in a project |
| GET | /tasks/:id | Get single task details |
| POST | /tasks | Create task |
| PUT | /tasks/:id | Update task (status, title, description, priority, assignee) |
| DELETE | /tasks/:id | Delete task (admin or creator) |
| GET | /comments?task_id= | List comments on a task |
| POST | /comments | Add comment |
| GET | /stats | Dashboard stats |

## User Roles

- **Admin** (project creator) — can edit/delete project, add/remove members, delete any task
- **Member** — can view project, create tasks, update own tasks, comment

## Limitation

Data is stored in memory only. Restarting the server clears all data. This is intentional for the MVP — the next step would be PostgreSQL (or SQLite for simplicity).
