"""Gestor de Tarefas - Prova de Suficiência Fábrica de Software UTFPR-DV.

Backend em Flask com SQLite. Autenticação baseada em sessão.
"""
import os
import re
import secrets
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TITLE_MAX = 200
DESCRIPTION_MAX = 2000


def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("DATABASE", os.path.join(BASE_DIR, "database.db")),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    # ---------------- Banco de dados ----------------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
            db = sqlite3.connect(app.config["DATABASE"])
            db.executescript(f.read())
            db.close()

    init_db()

    # ---------------- Utilitários ----------------
    def error(message, status):
        return jsonify({"error": message}), status

    def get_json():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else None

    def task_to_dict(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "created_at": row["created_at"],
        }

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("user_id") is None:
                return error("Autenticação necessária.", 401)
            return view(*args, **kwargs)
        return wrapped

    def validate_task(data):
        """Retorna (title, description, mensagem_de_erro)."""
        title = data.get("title")
        description = data.get("description", "")
        if description is None:
            description = ""
        if not isinstance(title, str) or not title.strip():
            return None, None, "O título é obrigatório."
        if not isinstance(description, str):
            return None, None, "Descrição inválida."
        title, description = title.strip(), description.strip()
        if len(title) > TITLE_MAX:
            return None, None, f"O título deve ter no máximo {TITLE_MAX} caracteres."
        if len(description) > DESCRIPTION_MAX:
            return None, None, f"A descrição deve ter no máximo {DESCRIPTION_MAX} caracteres."
        return title, description, None

    def find_own_task(task_id):
        # Filtra pelo usuário logado: tarefas de outros usuários resultam em 404.
        return get_db().execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, session["user_id"]),
        ).fetchone()

    # ---------------- Frontend ----------------
    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    # ---------------- Autenticação ----------------
    @app.post("/api/auth/register")
    def register():
        data = get_json()
        if data is None:
            return error("Envie os dados em JSON.", 400)
        name = str(data.get("name") or "").strip()
        email = str(data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not name:
            return error("O nome é obrigatório.", 400)
        if not EMAIL_RE.match(email):
            return error("Informe um e-mail válido.", 400)
        if not isinstance(password, str) or len(password) < 6:
            return error("A senha deve ter pelo menos 6 caracteres.", 400)

        db = get_db()
        try:
            cur = db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return error("Este e-mail já está cadastrado.", 409)

        session.clear()
        session["user_id"] = cur.lastrowid
        return jsonify({"id": cur.lastrowid, "name": name, "email": email}), 201

    @app.post("/api/auth/login")
    def login():
        data = get_json()
        if data is None:
            return error("Envie os dados em JSON.", 400)
        email = str(data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], str(password)):
            return error("E-mail ou senha inválidos.", 401)
        session.clear()
        session["user_id"] = user["id"]
        return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return "", 204

    @app.get("/api/auth/me")
    @login_required
    def me():
        user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        if user is None:
            session.clear()
            return error("Autenticação necessária.", 401)
        return jsonify(dict(user))

    # ---------------- Tarefas (CRUD) ----------------
    @app.get("/api/tasks")
    @login_required
    def list_tasks():
        rows = get_db().execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at ASC, id ASC",
            (session["user_id"],),
        ).fetchall()
        return jsonify([task_to_dict(r) for r in rows])

    @app.post("/api/tasks")
    @login_required
    def create_task():
        data = get_json()
        if data is None:
            return error("Envie os dados em JSON.", 400)
        title, description, msg = validate_task(data)
        if msg:
            return error(msg, 400)
        db = get_db()
        cur = db.execute(
            "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description),
        )
        db.commit()
        return jsonify(task_to_dict(find_own_task(cur.lastrowid))), 201

    @app.get("/api/tasks/<int:task_id>")
    @login_required
    def get_task(task_id):
        task = find_own_task(task_id)
        if task is None:
            return error("Tarefa não encontrada.", 404)
        return jsonify(task_to_dict(task))

    @app.put("/api/tasks/<int:task_id>")
    @login_required
    def update_task(task_id):
        if find_own_task(task_id) is None:
            return error("Tarefa não encontrada.", 404)
        data = get_json()
        if data is None:
            return error("Envie os dados em JSON.", 400)
        title, description, msg = validate_task(data)
        if msg:
            return error(msg, 400)
        db = get_db()
        db.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ? AND user_id = ?",
            (title, description, task_id, session["user_id"]),
        )
        db.commit()
        return jsonify(task_to_dict(find_own_task(task_id)))

    @app.delete("/api/tasks/<int:task_id>")
    @login_required
    def delete_task(task_id):
        db = get_db()
        cur = db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, session["user_id"]),
        )
        db.commit()
        if cur.rowcount == 0:
            return error("Tarefa não encontrada.", 404)
        return "", 204

    # ---------------- Erros genéricos da API ----------------
    @app.errorhandler(404)
    def not_found(_e):
        return error("Recurso não encontrado.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return error("Método não permitido.", 405)

    @app.errorhandler(500)
    def internal_error(_e):
        return error("Erro interno do servidor.", 500)

    return app


if __name__ == "__main__":
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")
