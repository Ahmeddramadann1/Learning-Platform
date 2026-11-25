
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import html


class LessonHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if urlparse(self.path).path == "/lesson":
            self.show_lesson()
        else:
            super().do_GET()

    def show_lesson(self):
        query = parse_qs(urlparse(self.path).query)
        lesson_id = query.get("id", [""])[0]

        if not lesson_id.isdigit():
            self.send_error(400, "Invalid lesson ID")
            return

        connection = sqlite3.connect("database/learning.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT title, video_url FROM lessons WHERE id = ?",
            (lesson_id,)
        )

        lesson = cursor.fetchone()
        connection.close()

        if lesson is None:
            self.send_error(404, "Lesson not found")
            return

        title = html.escape(lesson[0])
        video_url = html.escape(lesson[1], quote=True)

        with open("lesson.html", "r", encoding="utf-8") as file:
            page = file.read()

        page = page.replace("{{LESSON_TITLE}}", title)
        page = page.replace("{{VIDEO_URL}}", video_url)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


server = HTTPServer(("127.0.0.1", 8000), LessonHandler)

print("Server is running at http://127.0.0.1:8000")

server.serve_forever()
