"""
PostgreSQL Schema for Production Deployment

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255)
);

CREATE TABLE projects(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    user_id INT REFERENCES users(id)
);

CREATE TABLE tasks(
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    status VARCHAR(50),
    priority VARCHAR(50),
    project_id INT REFERENCES projects(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE comments(
    id SERIAL PRIMARY KEY,
    comment TEXT,
    task_id INT REFERENCES tasks(id),
    user_id INT REFERENCES users(id)
);
"""
