def make_user(id, username, email, password):
    return {
        "id": id,
        "username": username,
        "email": email,
        "password": password,
    }


def make_project(id, name, description, user_id):
    return {
        "id": id,
        "name": name,
        "description": description,
        "user_id": user_id,
    }


def make_task(id, title, description, status, priority, project_id, user_id):
    return {
        "id": id,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "project_id": project_id,
        "user_id": user_id,
    }


def make_comment(id, task_id, user_id, comment):
    return {
        "id": id,
        "task_id": task_id,
        "user_id": user_id,
        "comment": comment,
    }
