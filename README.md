# Team Task Management System

A simple project management app like Jira or Trello.

Teams can create projects, add members, assign tasks, and track progress.

## What You Need

- Python installed on your computer
- Node.js installed on your computer

## How to Run the Project

### Step 1: Start the Backend (Server)

Open a terminal and run these commands:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

You should see: `Running on http://localhost:5000`

Keep this terminal window open.

### Step 2: Start the Frontend (Website)

Open a second terminal and run:

```bash
cd frontend
npm install
npm run dev
```

You should see: `http://localhost:5173`

Open that link in your browser.

### Demo Account

You can also create your own account.

- **Email**: `demo@test.com`
- **Password**: `pass`

## What You Can Do

- **Register** — Create an account
- **Login** — Sign in to the app
- **Dashboard** — See your projects and stats
- **Create Project** — Start a new project
- **Add Members** — Invite people to your project
- **Create Tasks** — Add tasks like "Build Login Page"
- **Assign Tasks** — Give a task to a team member
- **Move Tasks** — Change status from Todo to In Progress to Review to Done
- **Add Comments** — Discuss a task
- **Edit Project** — Change the name or description
- **Delete Project** — Remove a project (only the owner)
- **Logout** — Sign out of the app

## Files in This Project

```
backend/
  app.py              The server code (Python/Flask)
  requirements.txt    Python packages needed

frontend/
  src/
    App.jsx           Main page (routes)
    Login.jsx         Login and Register page
    Dashboard.jsx     Home page with projects and stats
    ProjectPage.jsx   Kanban board with tasks and members
    TaskPage.jsx      Task details with comments
    App.css           Styles for the website
```

## Important Note

All data is stored in the computer's memory. If you stop the server and start it again, all your data will be gone. This is fine for a school project or demo. For a real app, you would add a database.
