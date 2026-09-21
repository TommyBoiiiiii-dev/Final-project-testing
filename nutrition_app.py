from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import sqlite3

ROOT = Path(__file__).parent
DB_PATH = ROOT / "nutrition.db"
STATIC_DIR = ROOT / "static"

FIELDS = [
    "name", "brand", "barcode", "serving_size", "servings_per_container",
    "calories", "energy_kj", "total_fat_g", "saturated_fat_g",
    "carbohydrates_g", "sugars_g", "fiber_g", "protein_g", "sodium_mg",
    "salt_g", "notes"
]


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT DEFAULT '',
                barcode TEXT DEFAULT '',
                serving_size TEXT NOT NULL,
                servings_per_container REAL,
                calories REAL,
                energy_kj REAL,
                total_fat_g REAL,
                saturated_fat_g REAL,
                carbohydrates_g REAL,
                sugars_g REAL,
                fiber_g REAL,
                protein_g REAL,
                sodium_mg REAL,
                salt_g REAL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def list_foods():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM foods ORDER BY created_at DESC, id DESC"
        ).fetchall()
        foods = [dict(row) for row in rows]
        print(f"Fetched {len(foods)} food entries from SQLite")
        return foods


def create_food(payload):
    missing = [field for field in ("name", "serving_size") if not str(payload.get(field, "")).strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    values = [payload.get(field, "") for field in FIELDS]
    with get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO foods ({', '.join(FIELDS)}) VALUES ({', '.join('?' for _ in FIELDS)})",
            values,
        )
        row = connection.execute("SELECT * FROM foods WHERE id = ?", (cursor.lastrowid,)).fetchone()
        print(f"Inserted food record id={cursor.lastrowid} name={payload.get('name', '')!r}")
        return dict(row)


class NutritionHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        print(f"GET {path}")
        if path == "/api/foods":
            foods = list_foods()
            self.send_json(200, {"foods": foods})
            print(f"Responded to GET {path} with {len(foods)} foods")
            return
        if path == "/" or path == "/index.html":
            self.serve_static("index.html", "text/html; charset=utf-8")
            print(f"Served index page for {path}")
            return
        if path.startswith("/static/"):
            filename = path.removeprefix("/static/")
            content_type = "text/css; charset=utf-8" if filename.endswith(".css") else "application/javascript; charset=utf-8"
            self.serve_static(filename, content_type)
            print(f"Served static asset: {filename}")
            return
        self.send_json(404, {"error": "Not found"})
        print(f"404 for GET {path}")

    def do_POST(self):
        path = urlparse(self.path).path
        print(f"POST {path}")
        if path != "/api/foods":
            self.send_json(404, {"error": "Not found"})
            print(f"404 for POST {path}")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            print(f"Received POST body: {raw.decode('utf-8', errors='replace')}")
            payload = json.loads(raw)
            food = create_food(payload)
            self.send_json(201, {"food": food})
            print(f"Created new food entry: {food.get('name')} (id={food.get('id')})")
        except (ValueError, json.JSONDecodeError) as error:
            print(f"POST validation error: {error}")
            self.send_json(400, {"error": str(error)})
        except sqlite3.Error as error:
            print(f"Database error on POST: {error}")
            self.send_json(500, {"error": f"Database error: {error}"})

    def serve_static(self, filename, content_type):
        requested = (STATIC_DIR / filename).resolve()
        if STATIC_DIR.resolve() not in requested.parents or not requested.is_file():
            self.send_json(404, {"error": "Not found"})
            return
        body = requested.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    init_database()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), NutritionHandler)
    print("Smart Nutrition is running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server.server_close()
