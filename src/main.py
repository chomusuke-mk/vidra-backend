import os
import sys
import traceback

# =============================================================================
# 0. REDIRECCIÓN TEMPRANA DE LOGS (SISTEMA DE CAJA NEGRA)
# =============================================================================
# Capturamos la variable antes que nada para atrapar errores de importación
SERVER_LOGS_FILE_PATH = os.path.abspath(
    os.environ.get("SERVER_LOGS_FILE_PATH", "./temp/logs/server.log")
)
os.makedirs(os.path.dirname(SERVER_LOGS_FILE_PATH), exist_ok=True)


class LoggerWriter:
    def __init__(self, filename):
        # Usamos append ("a") para no borrar el historial si se reinicia rápido
        self.filename = filename

    def write(self, message):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(message)
            f.flush()  # Forzamos la escritura inmediata en disco

    def flush(self):
        pass

    def close(self):
        pass


# Redirigimos la salida estándar (print) y la de errores (excepciones/Tracebacks)
sys.stdout = LoggerWriter(SERVER_LOGS_FILE_PATH)
sys.stderr = sys.stdout

# =============================================================================
# 1. EJECUCIÓN PRINCIPAL ENVUELTA EN TRY-EXCEPT
# =============================================================================
try:
    print("\n" + "=" * 10)
    print("Iniciando entorno Python")
    print("-" * 10)
    import logging
    import threading
    from functools import wraps

    import certifi

    # --- 1. OBTENER VARIABLES DEL ENTORNO (INYECCIÓN DEL CONTENEDOR PADRE) ---
    ENV = os.environ.get("APP_ENV", "development")
    API_TOKEN = os.environ.get("API_TOKEN", "SUPER_SECRET_TOKEN")
    LOGS_PATH = os.path.abspath(os.environ.get("LOGS_PATH", "./temp/logs"))
    DATA_PATH = os.path.abspath(os.environ.get("DATA_PATH", "./temp/data"))
    TEMP_PATH = os.path.abspath(os.environ.get("TEMP_PATH", "./temp/temp"))
    FFMPEG_PATH = os.path.abspath(os.environ.get("FFMPEG_PATH", "./temp/ffmpeg"))
    FFPROBE_PATH = os.path.join(
        os.path.dirname(FFMPEG_PATH),
        os.path.basename(FFMPEG_PATH).replace("ffmpeg", "ffprobe"),
    )
    QUICKJS_PATH = os.path.abspath(os.environ.get("QUICKJS_PATH", "./temp/quickjs"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    CORE_MODULES_PATH = os.path.abspath(
        os.environ.get("CORE_MODULES_PATH", "./temp/core_modules")
    )

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # --- CONFIGURACIÓN DE CERTIFICADOS Y RUTAS ---
    cert_path = certifi.where()
    os.environ["SSL_CERT_FILE"] = cert_path
    os.environ["REQUESTS_CA_BUNDLE"] = cert_path
    if sys.platform == "linux":
        os.environ.setdefault("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        os.environ.setdefault("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    else:
        os.environ.setdefault("XDG_CONFIG_HOME", os.path.join(DATA_PATH, "yt-dlp"))
        os.environ.setdefault("XDG_CACHE_HOME", os.path.join(TEMP_PATH, "yt-dlp"))
    os.makedirs(os.environ["XDG_CONFIG_HOME"], exist_ok=True)
    os.makedirs(os.environ["XDG_CACHE_HOME"], exist_ok=True)
    logging.basicConfig(level=LOG_LEVEL)

    # --- CREACIÓN DE SYMBOLIC LINKS PARA FFMPEG ---
    os.makedirs(os.path.join(TEMP_PATH, "binaries"), exist_ok=True)
    if os.path.exists(os.path.join(TEMP_PATH, "binaries", "ffmpeg")):
        os.remove(os.path.join(TEMP_PATH, "binaries", "ffmpeg"))
    if os.path.exists(os.path.join(TEMP_PATH, "binaries", "ffprobe")):
        os.remove(os.path.join(TEMP_PATH, "binaries", "ffprobe"))
    if os.path.exists(os.path.join(TEMP_PATH, "binaries", "quickjs")):
        os.remove(os.path.join(TEMP_PATH, "binaries", "quickjs"))
    os.symlink(FFMPEG_PATH, os.path.join(TEMP_PATH, "binaries", "ffmpeg"))
    os.symlink(FFPROBE_PATH, os.path.join(TEMP_PATH, "binaries", "ffprobe"))
    os.symlink(QUICKJS_PATH, os.path.join(TEMP_PATH, "binaries", "quickjs"))
    os.environ["PATH"] = (
        f"{os.path.join(TEMP_PATH, 'binaries')}{os.pathsep}{os.environ.get('PATH', '')}"
    )

    # --- PRINT DE VARIABLES DE ENTORNO PARA DEBUGGING ---
    print("LOGS_PATH:", LOGS_PATH)
    print("DATA_PATH:", DATA_PATH)
    print("TEMP_PATH:", TEMP_PATH)
    print("FFMPEG_PATH:", FFMPEG_PATH)
    print("FFPROBE_PATH:", FFPROBE_PATH)
    print("QUICKJS_PATH:", QUICKJS_PATH)
    print("Current platform:", sys.platform)
    print("XDG_CONFIG_HOME:", os.environ["XDG_CONFIG_HOME"])
    print("XDG_CACHE_HOME:", os.environ["XDG_CACHE_HOME"])
    print("Current LOG_LEVEL:", LOG_LEVEL)

    # --- INICIALIZACIÓN DEL SERVIDOR Y APLICACIÓN ---
    from flask import Flask, Response, jsonify, request

    from app import App
    from ota_manager import OTAManager

    server = Flask(__name__)
    ota_manager = OTAManager(CORE_MODULES_PATH)

    # 2. CONFIGURAR FLASK
    if ENV == "production":
        server.config["DEBUG"] = False
        server.config["TESTING"] = False
        server.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

    app = App(
        logs_path=LOGS_PATH,
        data_path=DATA_PATH,
        temp_path=TEMP_PATH,
        ffmpeg_path=FFMPEG_PATH,
        quickjs_path=QUICKJS_PATH,
    )

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
    @token_required
    def health_check():
        return jsonify(
            {
                "status": "ok"
                if ota_manager.get_status() == "load"
                else ota_manager.get_status()
            }
        )

    @server.route("/ota", methods=["PATCH"])
    @token_required
    def ota_control():
        action = (request.args.get("action") or "").lower().strip()
        if action != "load" and action != "unload":
            return jsonify({"error": "Invalid action, must be 'load' or 'unload'"}), 400
        try:
            if action == "load":
                ota_manager.load()
            elif action == "unload":
                app.stop_running_downloads()
                ota_manager.unload()
            return jsonify({"message": "OTA control applied."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @server.route("/favicon.ico")
    @token_required
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
        return jsonify(
            {"message": "Download added successfully", "id": download_id}
        ), 201

    @server.route("/downloads", methods=["PATCH"])
    @token_required
    def update_downloads():
        action = request.args.get("action")
        download_id = request.args.get("id")
        if not download_id:
            return jsonify({"error": "ID is required"}), 400
        if not action:
            return jsonify({"error": "Action is required"}), 400
        if (
            action != "pause"
            and action != "resume"
            and action != "cancel"
            and action != "delete"
            and action != "retry"
        ):
            return jsonify(
                {
                    "error": "Invalid action, must be one of 'pause', 'resume', 'cancel', 'delete', 'retry'"
                }
            ), 400
        try:
            app.update_download(id=download_id, action=action)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"message": f"Action {action} performed successfully"}), 200

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
        if not isinstance(entries, list) or not all(
            isinstance(e, str) for e in entries
        ):
            return jsonify({"error": "Entries must be a list of strings(IDS)"}), 400
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

    def init_ota_tasks():
        ota_manager.snapshot()
        ota_manager.load()

    # Creamos y arrancamos el hilo justo antes del bloqueo del servidor
    # daemon=True asegura que si el servidor principal se apaga, este hilo no impida que la app se cierre.
    ota_thread = threading.Thread(target=init_ota_tasks, daemon=True)
    ota_thread.start()

    if ENV != "production":
        server.run(debug=True, port=PORT, host=HOST)
    else:
        from waitress import serve

        print(f"Iniciando Waitress en {HOST}:{PORT} con 16 hilos...")
        serve(server, host=HOST, port=PORT, threads=16)

except Exception:
    # Si cualquier cosa falla (ej: módulo no encontrado), lo mandamos al archivo log antes de morir.
    print("\n!!! ERROR FATAL DURANTE EL ARRANQUE DEL SERVIDOR !!!")
    traceback.print_exc()
finally:
    print("\n" + "=" * 50)
    print("Servidor Python finalizado.")
    print("=" * 50)
    sys.stderr = os.devnull
    sys.stdout.close()
    sys.stdout = os.devnull
