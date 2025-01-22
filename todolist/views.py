import sqlite3
from sqlite3 import IntegrityError

from flask import Blueprint, render_template, request, redirect, flash, session
from .variables import db_path

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/login')
def login():
    return render_template('login.html')

@views.route('/register')
def register():
    return render_template('register.html')


@views.route('/adduser', methods=['POST'])
def adduser():
    username = request.form.get('username')
    password = request.form.get('password')

    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute(
                "INSERT INTO credentials (username, password) VALUES (?, ?);",
                (username, password)
            )
            conn.commit()
        except IntegrityError:
            flash("Username already exists")
            return redirect('/register')
    return redirect('/login')

@views.route('/validation', methods=['POST'])
def validation():
    username = request.form.get('username')
    password = request.form.get('password')

    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            """
            SELECT username, password
            FROM credentials 
            WHERE username = ?;
            """, (username,)
        ).fetchone()

    if result and password == result[1]:
        session['username'] = username  # Store the username in the session
        return redirect('/todolist')  # Redirect to the todolist
    else:
        flash("Invalid username or password")
        return redirect('/login')

@views.route('/todolist')
def todolist():
    username = session.get('username')

    with sqlite3.connect(db_path) as conn:
        conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {username} (
                    task TEXT UNIQUE NOT NULL,
                    description TEXT,
                    due DATETIME NOT NULL
                );
            """)
        result = conn.execute(
            f"""
            SELECT task, description, due
            FROM {username}
            ORDER BY due ASC
            """
        ).fetchall()
    return render_template('todolist.html', username=username, tasks=result)

@views.route('/addtask', methods=['POST'])
def addtask():
    username = session.get("username")
    task = request.form.get('task')
    description = request.form.get('description')
    due = request.form.get('due')

    with sqlite3.connect(db_path) as conn:
        conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS {username} (
                            task TEXT UNIQUE NOT NULL,
                            description TEXT,
                            due DATETIME NOT NULL
                        );
                    """)
        try:
            conn.execute(
                f"INSERT INTO {username} (task, description, due) VALUES (?, ?, ?);",
                (task, description, due)
            )
            conn.commit()
        except IntegrityError:
            flash("Task already exists")
            return redirect('/todolist')
    return redirect('/todolist')

@views.route('/removetask', methods=['POST'])
def removetask():
    task = request.form.get("task")
    username = session.get("username")

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f"""
            DELETE FROM {username}
            WHERE task=?;
            """, (task,))
    return redirect('/todolist')