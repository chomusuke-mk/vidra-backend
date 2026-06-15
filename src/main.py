from flask import Flask, jsonify, request, Response
from functools import wraps
import certifi
import os
from app import App

# --- 1. OBTENER VARIABLES DEL ENTORNO (INYECCIÓN DEL CONTENEDOR PADRE) ---
ENV = os.environ.get("APP_ENV", "development")
API_TOKEN = os.environ.get("API_TOKEN", "SUPER_SECRET_TOKEN")
LOGS_PATH = os.environ.get("LOGS_PATH", "./temp/logs")
DATA_PATH = os.environ.get("DATA_PATH", "./temp/data")
TEMP_PATH = os.environ.get("TEMP_PATH", "./temp/temp")

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))

# --- CONFIGURACIÓN DE CERTIFICADOS Y RUTAS ---
cert_path = certifi.where()
os.environ["SSL_CERT_FILE"] = cert_path
os.environ["REQUESTS_CA_BUNDLE"] = cert_path
os.environ["XDG_CONFIG_HOME"] = os.path.join(DATA_PATH, "yt-dlp")
os.environ["XDG_CACHE_HOME"] = os.path.join(TEMP_PATH, "yt-dlp")

# --- INICIALIZACIÓN DEL SERVIDOR Y APLICACIÓN ---
server = Flask(__name__)

# 2. CONFIGURAR FLASK
if ENV == "production":
    server.config["DEBUG"] = False
    server.config["TESTING"] = False
    server.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

app = App(logs_path=LOGS_PATH, data_path=DATA_PATH, temp_path=TEMP_PATH)


# --- SEGURIDAD ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if ENV == "production" and (not token or token != API_TOKEN):
            return jsonify({"error": "Invalid or missing API token"}), 401
        return f(*args, **kwargs)

    return decorated


# --- RUTAS ---
@server.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@server.route("/favicon.ico")
def favicon():
    svg_content = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect width="100" height="100" fill="black"/>
        <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="70" font-weight="bold">V</text>
    </svg>
    """
    return Response(svg_content, mimetype="image/svg+xml")


@server.route("/logs", methods=["GET"])
@token_required
def get_logs():
    download_id = request.args.get("id")
    try:
        logs = app.get_logs(id=download_id)
        return Response(logs, mimetype="text/plain")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


@server.route("/downloads", methods=["GET"])
@token_required
def get_info():
    download_id = request.args.get("id")
    try:
        info = app.get_downloads(id=download_id)
        return jsonify(info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


@server.route("/downloads", methods=["POST"])
@token_required
def add_download():
    data = request.get_json()
    url = data.get("url", "")
    options = data.get("options", {})
    if not url:
        return jsonify({"error": "URL is required"}), 400
    download_id = app.add_download(url=url, options=options)
    return jsonify({"message": "Download added successfully", "id": download_id}), 201


@server.route("/downloads", methods=["PATCH"])
@token_required
def update_downloads():
    action = request.args.get("action")
    download_id = request.args.get("id")
    if not download_id:
        return jsonify({"error": "ID is required"}), 400
    if not action:
        return jsonify({"error": "Action is required"}), 400
    if action not in ["pause", "resume", "cancel", "retry"]:
        return jsonify(
            {
                "error": "Invalid action, must be one of 'pause', 'resume', 'cancel' or 'retry'"
            }
        ), 400
    # TODO: implement pause, resume, cancel and retry actions
    return jsonify({"error": f"Action {action} not implemented yet"}), 501


@server.route("/select-entries", methods=["GET"])
@token_required
def get_entries_to_select():
    download_id = request.args.get("id")

    if not download_id:
        return jsonify({"error": "ID is required"}), 400
    try:
        entries = app.get_entries_to_select(id=download_id)
        return jsonify({"entries": entries})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


@server.route("/select-entries", methods=["POST"])
@token_required
def select_entries():
    download_id = request.args.get("id")
    entries = request.get_json().get("entries")
    if not download_id or not entries:
        return jsonify({"error": "ID and entries are required"}), 400
    try:
        app.select_entries(id=download_id, entries=entries)
        return jsonify({"message": "Entries selected successfully"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


@server.route("/subscribe", methods=["GET"])
@token_required
def subscribe_to_deltas():
    download_id = request.args.get("id")
    everything = request.args.get("everything", "false").lower() == "true"
    try:
        return Response(
            app.subscribe_to_deltas(id=download_id, everything=everything),
            mimetype="text/event-stream",
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


if ENV != "production":
    server.run(debug=True, port=PORT, host=HOST)
else:
    from waitress import serve

    print(f"Iniciando Waitress en {HOST}:{PORT} con 2 hilos...")
    serve(server, host=HOST, port=PORT, threads=2)
