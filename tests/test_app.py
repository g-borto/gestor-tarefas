"""Testes funcionais dos fluxos obrigatórios. Executar com:
    python -m unittest discover -s tests -v
"""
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app  # noqa: E402


class AppTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path, "SECRET_KEY": "test"})
        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.db_path)

    def register(self, client=None, email="ana@exemplo.com", name="Ana", password="segredo123"):
        client = client or self.client
        return client.post("/api/auth/register",
                           json={"name": name, "email": email, "password": password})

    # ---------- Autenticação ----------
    def test_register_login_logout(self):
        r = self.register()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["email"], "ana@exemplo.com")

        self.assertEqual(self.client.post("/api/auth/logout").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

        r = self.client.post("/api/auth/login",
                             json={"email": "ana@exemplo.com", "password": "segredo123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me").get_json()["name"], "Ana")

    def test_login_wrong_password(self):
        self.register()
        self.client.post("/api/auth/logout")
        r = self.client.post("/api/auth/login",
                             json={"email": "ana@exemplo.com", "password": "errada"})
        self.assertEqual(r.status_code, 401)

    def test_register_validation_and_duplicate(self):
        self.assertEqual(self.client.post("/api/auth/register",
                         json={"name": "", "email": "a@b.com", "password": "123456"}).status_code, 400)
        self.assertEqual(self.client.post("/api/auth/register",
                         json={"name": "A", "email": "invalido", "password": "123456"}).status_code, 400)
        self.assertEqual(self.client.post("/api/auth/register",
                         json={"name": "A", "email": "a@b.com", "password": "123"}).status_code, 400)
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.register(email="ANA@exemplo.com").status_code, 409)

    def test_password_is_hashed(self):
        self.register()
        db = sqlite3.connect(self.db_path)
        stored = db.execute("SELECT password_hash FROM users").fetchone()[0]
        db.close()
        self.assertNotEqual(stored, "segredo123")
        self.assertNotIn("segredo123", stored)

    def test_routes_require_authentication(self):
        for method, url in [("get", "/api/tasks"), ("post", "/api/tasks"),
                            ("get", "/api/tasks/1"), ("put", "/api/tasks/1"),
                            ("delete", "/api/tasks/1")]:
            r = getattr(self.client, method)(url, json={"title": "x"})
            self.assertEqual(r.status_code, 401, f"{method.upper()} {url}")

    # ---------- CRUD ----------
    def test_task_crud_and_order(self):
        self.register()
        r = self.client.post("/api/tasks", json={"title": "Primeira", "description": "Desc 1"})
        self.assertEqual(r.status_code, 201)
        t1 = r.get_json()
        r = self.client.post("/api/tasks", json={"title": "Segunda"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["description"], "")
        self.client.post("/api/tasks", json={"title": "Terceira"})

        titles = [t["title"] for t in self.client.get("/api/tasks").get_json()]
        self.assertEqual(titles, ["Primeira", "Segunda", "Terceira"])

        r = self.client.get(f"/api/tasks/{t1['id']}")
        self.assertEqual(r.get_json()["description"], "Desc 1")

        r = self.client.put(f"/api/tasks/{t1['id']}", json={"title": "Editada", "description": "Nova"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["title"], "Editada")

        self.assertEqual(self.client.delete(f"/api/tasks/{t1['id']}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/tasks/{t1['id']}").status_code, 404)
        self.assertEqual(len(self.client.get("/api/tasks").get_json()), 2)

    def test_title_required(self):
        self.register()
        for payload in [{}, {"title": ""}, {"title": "   "}, {"title": None}, {"title": 123}]:
            self.assertEqual(self.client.post("/api/tasks", json=payload).status_code, 400, payload)
        task = self.client.post("/api/tasks", json={"title": "Ok"}).get_json()
        r = self.client.put(f"/api/tasks/{task['id']}", json={"title": ""})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.post("/api/tasks", data="texto").status_code, 400)

    # ---------- Isolamento entre usuários ----------
    def test_user_cannot_access_other_users_tasks(self):
        self.register()
        task = self.client.post("/api/tasks", json={"title": "Da Ana"}).get_json()

        other = self.app.test_client()
        self.register(client=other, email="bruno@exemplo.com", name="Bruno")
        self.assertEqual(other.get("/api/tasks").get_json(), [])
        self.assertEqual(other.get(f"/api/tasks/{task['id']}").status_code, 404)
        self.assertEqual(other.put(f"/api/tasks/{task['id']}", json={"title": "Hack"}).status_code, 404)
        self.assertEqual(other.delete(f"/api/tasks/{task['id']}").status_code, 404)

        # A tarefa da Ana continua intacta.
        self.assertEqual(self.client.get(f"/api/tasks/{task['id']}").get_json()["title"], "Da Ana")

    # ---------- Persistência ----------
    def test_data_persists_after_restart(self):
        self.register()
        self.client.post("/api/tasks", json={"title": "Persistente"})

        app2 = create_app({"TESTING": True, "DATABASE": self.db_path, "SECRET_KEY": "outra"})
        client2 = app2.test_client()
        r = client2.post("/api/auth/login",
                         json={"email": "ana@exemplo.com", "password": "segredo123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual([t["title"] for t in client2.get("/api/tasks").get_json()], ["Persistente"])

    def test_frontend_is_served(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Gestor de Tarefas", r.data)
        r.close()


if __name__ == "__main__":
    unittest.main()
