import hashlib
import hmac
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

project_folder = Path(__file__).resolve().parent.parent
database_folder = project_folder / "database"
database_file = database_folder / "learning.db"
sessions = {}


def prepare_database():
    with sqlite3.connect(database_file) as db:
        table = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'students'"
        ).fetchone()

        if table is None:
            schema = (database_folder / "schema.sql").read_text(encoding="utf-8")
            db.executescript(schema)


def hash_password(password, salt):
    return hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1
    ).hex()


class AuthHandler(BaseHTTPRequestHandler):
    def reply(self, status, message, token=None):
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if token:
            self.send_header(
                "Set-Cookie", f"session={token}; Path=/; HttpOnly; SameSite=Lax"
            )
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path not in ("/register", "/login"):
            self.reply(404, "Page not found.")
            return

        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            self.reply(415, "Please submit an HTML form.")
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                self.reply(400, "Invalid form size.")
                return
            form = parse_qs(self.rfile.read(size).decode("utf-8"))
        except ValueError:
            self.reply(400, "Invalid form.")
            return

        email = form.get("email", [""])[0].strip().lower()
        password = form.get("password", [""])[0]

        if not email or not password:
            self.reply(400, "Enter your email and password.")
            return

        if self.path == "/register":
            name = form.get("name", [""])[0].strip()
            self.register(name, email, password)
        else:
            self.login(email, password)

    def register(self, name, email, password):
        if not name:
            self.reply(400, "Enter your name.")
            return

        salt = secrets.token_bytes(16)
        password_hash = salt.hex() + ":" + hash_password(password, salt)

        try:
            with sqlite3.connect(database_file) as db:
                db.execute(
                    "INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, password_hash)
                )
        except sqlite3.IntegrityError:
            self.reply(409, "This email is already registered.")
            return

        self.reply(201, "Account created successfully.")

    def login(self, email, password):
        with sqlite3.connect(database_file) as db:
            student = db.execute(
                "SELECT id, password_hash FROM students WHERE email = ?",
                (email,)
            ).fetchone()

        if student:
            salt, saved_hash = student[1].split(":", 1)
            entered_hash = hash_password(password, bytes.fromhex(salt))

            if hmac.compare_digest(saved_hash, entered_hash):
                token = secrets.token_urlsafe(32)
                sessions[token] = student[0]
                self.reply(200, "Login successful.", token)
                return

        self.reply(401, "Invalid email or password.")


if __name__ == "__main__":
    prepare_database()
    print("Server running at http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), AuthHandler).serve_forever()
