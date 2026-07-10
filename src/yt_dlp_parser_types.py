from typing import (
    Literal,
    Final,
    TypeGuard,
    Dict,
    NotRequired,
    List,
    Union,
    get_args,
    TypedDict,
    Any,
)

T_LANGUAGE = Literal[
    "aa",
    "ab",
    "ae",
    "af",
    "ak",
    "am",
    "an",
    "ar",
    "as",
    "av",
    "ay",
    "az",
    "ba",
    "be",
    "bg",
    "bi",
    "bm",
    "bn",
    "bo",
    "br",
    "bs",
    "ca",
    "ce",
    "ch",
    "co",
    "cr",
    "cs",
    "cu",
    "cv",
    "cy",
    "da",
    "de",
    "dv",
    "dz",
    "ee",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "ff",
    "fi",
    "fj",
    "fo",
    "fr",
    "fy",
    "ga",
    "gd",
    "gl",
    "gn",
    "gu",
    "gv",
    "ha",
    "he",
    "hi",
    "ho",
    "hr",
    "ht",
    "hu",
    "hy",
    "hz",
    "ia",
    "id",
    "ie",
    "ig",
    "ii",
    "ik",
    "io",
    "is",
    "it",
    "iu",
    "ja",
    "jv",
    "ka",
    "kg",
    "ki",
    "kj",
    "kk",
    "kl",
    "km",
    "kn",
    "ko",
    "kr",
    "ks",
    "ku",
    "kv",
    "kw",
    "ky",
    "la",
    "lb",
    "lg",
    "li",
    "ln",
    "lo",
    "lt",
    "lu",
    "lv",
    "mg",
    "mh",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "na",
    "nb",
    "nd",
    "ne",
    "ng",
    "nl",
    "nn",
    "no",
    "nr",
    "nv",
    "ny",
    "oc",
    "oj",
    "om",
    "or",
    "os",
    "pa",
    "pi",
    "pl",
    "ps",
    "pt",
    "qu",
    "rm",
    "rn",
    "ro",
    "ru",
    "rw",
    "sa",
    "sc",
    "sd",
    "se",
    "sg",
    "si",
    "sk",
    "sl",
    "sm",
    "sn",
    "so",
    "sq",
    "sr",
    "ss",
    "st",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "ti",
    "tk",
    "tl",
    "tn",
    "to",
    "tr",
    "ts",
    "tt",
    "tw",
    "ty",
    "ug",
    "uk",
    "ur",
    "uz",
    "ve",
    "vi",
    "vo",
    "wa",
    "wo",
    "xh",
    "yi",
    "yo",
    "za",
    "zh",
    "zu",
]

LANGUAGE: Final = get_args(T_LANGUAGE)

T_AUDIO_OPTIONS = Literal["bestaudio", T_LANGUAGE]
AUDIO_OPTIONS: Final = get_args(T_AUDIO_OPTIONS)

T_RESOLUTION = Literal[
    "144", "240", "360", "480", "720", "1080", "1440", "2160", "4320"
]
RESOLUTION: Final = get_args(T_RESOLUTION)

T_VIDEO_OPTIONS = Literal["bestvideo", T_RESOLUTION]
VIDEO_OPTIONS: Final = get_args(T_VIDEO_OPTIONS)

T_SUBTITLE_OPTIONS = Literal["none", T_LANGUAGE, "all"]
SUBTITLE_OPTIONS: Final = get_args(T_SUBTITLE_OPTIONS)

T_JS_RUNTIMES_KEYS = Literal["deno", "node", "quickjs", "bun"]
JS_RUNTIMES_KEYS: Final = get_args(T_JS_RUNTIMES_KEYS)

T_BROWSERS = Literal[
    "brave",
    "chrome",
    "chromium",
    "edge",
    "firefox",
    "opera",
    "safari",
    "vivaldi",
    "whale",
]
BROWSERS: Final = get_args(T_BROWSERS)

T_MERGE_OUTPUT_FORMATS = Literal["avi", "flv", "mkv", "mov", "mp4", "webm"]
MERGE_OUTPUT_FORMATS: Final = get_args(T_MERGE_OUTPUT_FORMATS)

T_AUDIO_FORMATS = Literal[
    "best", "aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"
]
AUDIO_FORMATS: Final = get_args(T_AUDIO_FORMATS)

T_AUDIO_QUALITY = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
AUDIO_QUALITY: Final = get_args(T_AUDIO_QUALITY)

T_REMUX_VIDEO_FORMATS = Literal[
    "avi",
    "flv",
    "gif",
    "mkv",
    "mov",
    "mp4",
    "webm",
    "aac",
    "aiff",
    "alac",
    "flac",
    "m4a",
    "mka",
    "mp3",
    "ogg",
    "opus",
    "vorbis",
    "wav",
]
REMUX_VIDEO_FORMATS: Final = get_args(T_REMUX_VIDEO_FORMATS)

T_FIXUP_OPTIONS = Literal["never", "warn", "detect_or_warn", "force"]
FIXUP_OPTIONS: Final = get_args(T_FIXUP_OPTIONS)

T_THUMBNAIL_FORMATS = Literal["jpg", "png", "webp"]
THUMBNAIL_FORMATS: Final = get_args(T_THUMBNAIL_FORMATS)

T_SUB_FORMATS = Literal["ass", "srt", "vtt", "json"]
SUB_FORMATS: Final = get_args(T_SUB_FORMATS)

T_OUTPUT_TEMPLATE_VARIABLES = Literal[
    "id",
    "title",
    "fulltitle",
    "ext",
    "alt_title",
    "description",
    "display_id",
    "uploader",
    "uploader_id",
    "uploader_url",
    "license",
    "creators",
    "creator",
    "timestamp",
    "upload_date",
    "release_timestamp",
    "release_date",
    "release_year",
    "modified_timestamp",
    "modified_date",
    "channel",
    "channel_id",
    "channel_url",
    "channel_follower_count",
    "channel_is_verified",
    "location",
    "duration",
    "duration_string",
    "view_count",
    "concurrent_view_count",
    "like_count",
    "dislike_count",
    "repost_count",
    "average_rating",
    "comment_count",
    "age_limit",
    "live_status",
    "is_live",
    "was_live",
    "playable_in_embed",
    "availability",
    "media_type",
    "start_time",
    "end_time",
    "extractor",
    "extractor_key",
    "epoch",
    "autonumber",
    "video_autonumber",
    "n_entries",
    "playlist_id",
    "playlist_title",
    "playlist",
    "playlist_count",
    "playlist_index",
    "playlist_autonumber",
    "playlist_uploader",
    "playlist_uploader_id",
    "playlist_channel",
    "playlist_channel_id",
    "playlist_webpage_url",
    "webpage_url",
    "webpage_url_basename",
    "webpage_url_domain",
    "original_url",
    "categories",
    "tags",
    "cast",
    # Available for the video that belongs to some logical chapter or section:
    "chapter",
    "chapter_number",
    "chapter_id",
    # Available for the video that is an episode of some series or program:
    "series",
    "series_id",
    "season",
    "season_number",
    "season_id",
    "episode",
    "episode_number",
    "episode_id",
    # Available for the media that is a track or a part of a music album:
    "track",
    "track_number",
    "track_id",
    "artists",
    "artist",
    "genres",
    "genre",
    "composers",
    "composer",
    "album",
    "album_type",
    "album_artists",
    "album_artist",
    "disc_number",
    # Available only when using --download-sections and for chapter:
    # prefix when using --split-chapters for videos with internal chapters:
    "section_title",
    "section_number",
    "section_start",
    "section_end",
]
OUTPUT_TEMPLATE_VARIABLES: Final = get_args(T_OUTPUT_TEMPLATE_VARIABLES)

T_PATHS_KEYS = Literal[
    "home",
    "temp",
    "video",
    "audio",
    "subtitle",
    "thumbnail",
    "infojson",
    "pl_thumbnail",
    "description",
    "annotation",
    "chapter",
    "sponsor",
]
PATHS_KEYS: Final = get_args(T_PATHS_KEYS)

T_SPONSORBLOCK_CATEGORIES = Literal[
    "sponsor",
    "intro",
    "outro",
    "selfpromo",
    "preview",
    "filler",
    "interaction",
    "music_offtopic",
    "hook",
    "poi_highlight",
    "chapter",
]
SPONSORBLOCK_CATEGORIES: Final = get_args(T_SPONSORBLOCK_CATEGORIES)


class VidraOptions(TypedDict):
    # General Options ===========================================================================
    # Presets para descargar la mejor pista de audio disponible en ciertos idiomas.
    audio_language: NotRequired[Literal["default", T_AUDIO_OPTIONS]]
    # Presets para descargar la mejor pista de video disponible en ciertas resoluciones.
    video_resolution: NotRequired[Literal["default", T_VIDEO_OPTIONS]]
    # Idiomas de subtítulos a descargar (“en”, “es”, “all”, etc.).
    sub_langs: NotRequired[List[Literal["all", T_LANGUAGE]]]
    # Convierte los videos descargados a audio (usa ffmpeg).
    extract_audio: NotRequired[bool]
    # Indica si se descarga la lista completa (True) o solo un video (False).
    playlist: NotRequired[bool]
    # Categorías de SponsorBlock para crear capítulos (“all”, “intro”, “outro”, etc.).
    sponsorblock_mark: NotRequired[List[T_SPONSORBLOCK_CATEGORIES]]
    # Categorías de SponsorBlock para eliminar (“all”, “intro”, “outro”, etc.).
    sponsorblock_remove: NotRequired[List[T_SPONSORBLOCK_CATEGORIES]]
    # Ignora errores de descarga y continúa con el siguiente video.
    ignore_errors: NotRequired[bool]
    # Detiene el proceso de descarga si ocurre un error.
    abort_on_error: NotRequired[bool]
    # Imprime detalles de la descarga
    quiet: NotRequired[bool]
    # Usa archivos .part para descargas incompletas (True) o no los usa (False).
    use_part_files: NotRequired[bool]
    # Continúa descargas incompletas (True) o reinicia descargas incompletas (False).
    continue_download: NotRequired[bool]
    # Nombres de extractores a usar (separados por coma).("all","default",expresión regular)
    use_extractors: NotRequired[List[str]]
    # Lista los videos de una playlist sin descargarlos.
    flat_playlist: NotRequired[bool]
    # Network Options ===========================================================================
    # Proxy HTTP/HTTPS/SOCKS. Ejemplo: socks5://user:pass@127.0.0.1:1080
    proxy: NotRequired[str]
    # Tiempo máximo de espera para conexiones (segundos).
    socket_timeout: NotRequired[Union[int, Literal["infinite"]]]
    # Dirección IP del cliente para realizar la conexión.
    source_address: NotRequired[str]
    # Cliente a emular (chrome, chrome-110, firefox, edge, etc.).
    impersonate: NotRequired[str]
    # Fuerza el uso de IPv4.
    force_ipv4: NotRequired[bool]
    # Fuerza el uso de IPv6.
    force_ipv6: NotRequired[bool]
    # Permite usar URLs locales (file://). Desactivado por seguridad.
    enable_file_urls: NotRequired[bool]
    # Proxy usado para verificar IP en contenido con restricciones geográficas.
    geo_verification_proxy: NotRequired[str]
    # Valor del encabezado HTTP “X-Forwarded-For” para simular ubicación.
    xff: NotRequired[str]
    # Usa conexión HTTP en lugar de HTTPS (solo YouTube).
    prefer_insecure: NotRequired[bool]
    # Encabezados HTTP personalizados.
    add_headers: NotRequired[Dict[str, str]]
    # Archivo Netscape de cookies para autenticación.
    cookies: NotRequired[Union[str, Literal[False]]]
    # Carga cookies directamente de un navegador instalado.
    cookies_from_browser: NotRequired[
        Union[
            Literal[False],
            T_BROWSERS,
        ]
    ]
    # Usuario o correo para autenticación.
    username: NotRequired[str]
    # Contraseña del usuario.
    password: NotRequired[str]
    # Código 2FA (autenticación de dos factores).
    twofactor: NotRequired[str]
    # Contraseña específica de video (si aplica).
    video_password: NotRequired[str]
    # Video  ===========================================================================
    # Formato final para mezclar (“mp4”, “mkv”, “webm”, etc.).
    merge_output_format: NotRequired[T_MERGE_OUTPUT_FORMATS]
    # Formato del audio convertido (“mp3”, “flac”, “opus”, etc.).
    audio_format: NotRequired[T_AUDIO_FORMATS]
    # Formato preferido de subtítulos (“srt”, “vtt”, “ass”, etc.).
    sub_format: NotRequired[T_SUB_FORMATS]
    # Permite combinar múltiples streams de video.
    video_multistreams: NotRequired[bool]
    # Permite combinar múltiples streams de audio.
    audio_multistreams: NotRequired[bool]
    # Calidad del audio (0 mejor, 10 peor).
    audio_quality: NotRequired[T_AUDIO_QUALITY]
    # Cambia el contenedor del video sin recodificar.
    remux_video: NotRequired[Union[Literal[False], T_REMUX_VIDEO_FORMATS]]
    # Inserta subtítulos en el archivo final.
    embed_subs: NotRequired[bool]
    # Inserta miniaturas en el archivo final.
    embed_thumbnail: NotRequired[bool]
    # Inserta metadatos en el archivo final.
    embed_metadata: NotRequired[bool]
    # Inserta capítulos en el archivo final.
    embed_chapters: NotRequired[bool]
    # Inserta infojson en el archivo final.
    embed_info_json: NotRequired[bool]
    # Código de formato o expresión para selección (ver “FORMAT SELECTION”).
    format: NotRequired[Union[str, List[str], List[List[str]]]]
    # Escribe metadatos en atributos extendidos del sistema.
    xattrs: NotRequired[bool]
    # Corrige errores conocidos del archivo (“never”, “warn”, “force”).
    fixup: NotRequired[T_FIXUP_OPTIONS]
    # Ruta al ejecutable de ffmpeg o ffprobe.
    ffmpeg_location: NotRequired[str]
    # Convierte miniaturas al formato indicado (“jpg”, “png”, “webp”).
    convert_thumbnails: NotRequired[T_THUMBNAIL_FORMATS]
    # Descarga subtítulos manuales disponibles.
    write_subs: NotRequired[bool]
    # Descarga subtítulos generados automáticamente.
    write_auto_subs: NotRequired[bool]
    # Download Options ==========================================================================
    # Plantilla de nombre del archivo de salida.
    output: NotRequired[
        List[
            Union[
                str,
                T_OUTPUT_TEMPLATE_VARIABLES,
            ]
        ]
    ]
    # Directorios donde guardar los diferentes tipos de archivos.
    paths: NotRequired[
        Dict[
            T_PATHS_KEYS,
            str,
        ]
    ]
    # Ruta de archivo donde registrar los IDs descargados, para evitar duplicados.
    download_archive: NotRequired[Union[Literal[False], str]]
    # Ids de videos a descargar de la playlist
    playlist_ids: NotRequired[List[str] | Literal["ALL_ITEMS"]]
    # Fragmentos simultáneos a descargar (por defecto 1).
    concurrent_fragments: NotRequired[int]
    # Detiene la descarga si se encuentra un archivo ya existente.
    break_on_existing: NotRequired[bool]
    # Sanitizar los nombres de archivo para ser compatibles con Windows.
    windows_filenames: NotRequired[bool]
    # Cancela la descarga si algún fragmento no está disponible.
    abort_on_unavailable_fragments: NotRequired[bool]
    # Mantiene los fragmentos descargados tras finalizar.
    keep_fragments: NotRequired[bool]
    # Archivo con URLs a descargar (una por línea).
    batch_file: NotRequired[Union[Literal[False], str]]
    # Sobrescribe archivos existentes (por defecto True).
    force_overwrites: NotRequired[bool]
    # Guarda la miniatura del video en disco.
    write_thumbnail: NotRequired[bool]
    # Descarga las transmisiones en vivo desde el inicio, si es compatible.
    live_from_start: NotRequired[bool]
    # Espera a que un video programado esté disponible antes de descargarlo.
    wait_for_video: NotRequired[Union[Literal[False], int]]
    # Marca el video como visto (si el sitio lo soporta).
    mark_watched: NotRequired[bool]
    # Entorno de ejecución para scripts JavaScript (deno, node, quickjs, bun).
    js_runtimes: NotRequired[Dict[T_JS_RUNTIMES_KEYS, str]]
    # Número máximo de errores permitidos antes de saltar el resto de la playlist.
    skip_playlist_after_errors: NotRequired[Union[int, Literal["infinite"]]]
    # Reintentos en caso de error (por defecto 10).
    retries: NotRequired[Union[int, Literal["infinite"]]]
    # Reintentos por error de acceso a archivo (por defecto 3).
    file_access_retries: NotRequired[Union[int, Literal["infinite"]]]
    # Reintentos por fragmento fallido (por defecto 10).
    fragment_retries: NotRequired[Union[int, Literal["infinite"]]]
    # Reintentos en caso de error en el extractor (por defecto 3).
    extractor_retries: NotRequired[Union[int, Literal["infinite"]]]
    # Límite de velocidad, por ejemplo "500K" o "4.2M".
    limit_rate: NotRequired[Union[Literal[False], str]]


def is_valid_options(options: Any) -> TypeGuard[VidraOptions]:
    if not isinstance(options, dict):
        return False
    for key, value in options.items():
        if key == "video_resolution":
            if (
                not (isinstance(value, str) and value in VIDEO_OPTIONS)
                and value != "default"
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "audio_language":
            if (
                not (isinstance(value, str) and value in AUDIO_OPTIONS)
                and value != "default"
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "sub_langs":
            if not (
                isinstance(value, list)
                and all(
                    isinstance(item, str) and (item in LANGUAGE or item == "all")
                    for item in value
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "extract_audio":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "playlist":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "sponsorblock_mark":
            if not (
                isinstance(value, list)
                and all(
                    isinstance(item, str) and item in SPONSORBLOCK_CATEGORIES
                    for item in value
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "sponsorblock_remove":
            if not (
                isinstance(value, list)
                and all(
                    isinstance(item, str) and item in SPONSORBLOCK_CATEGORIES
                    for item in value
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "ignore_errors":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "abort_on_error":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "quiet":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "use_part_files":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "continue_download":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "use_extractors":
            if not (
                isinstance(value, list) and all(isinstance(item, str) for item in value)
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "flat_playlist":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "proxy":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "socket_timeout":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "source_address":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "impersonate":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "force_ipv4":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "force_ipv6":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "enable_file_urls":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "geo_verification_proxy":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "xff":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "prefer_insecure":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "add_headers":
            if not (
                isinstance(value, dict)
                and all(
                    isinstance(k, str) and isinstance(v, str) for k, v in value.items()
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "cookies":
            if not (isinstance(value, str) or value is False):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "cookies_from_browser":
            if (
                not (isinstance(value, str) and value in BROWSERS)
                and value is not False
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "username":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "password":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "twofactor":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "video_password":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "merge_output_format":
            if not (isinstance(value, str) and value in MERGE_OUTPUT_FORMATS):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "audio_format":
            if not (isinstance(value, str) and value in AUDIO_FORMATS):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "sub_format":
            if not isinstance(value, str) and value not in SUB_FORMATS:
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "video_multistreams":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "audio_multistreams":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "audio_quality":
            if not isinstance(value, int):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "remux_video":
            if (
                not (isinstance(value, str) and value in REMUX_VIDEO_FORMATS)
                and value is not False
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "embed_subs":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "embed_thumbnail":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "embed_metadata":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "embed_chapters":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "embed_info_json":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "format":
            if not (isinstance(value, str) or isinstance(value, list)):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "xattrs":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "fixup":
            if not (isinstance(value, str) and value in FIXUP_OPTIONS):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "ffmpeg_location":
            if not isinstance(value, str):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "convert_thumbnails":
            if not (isinstance(value, str) and value in THUMBNAIL_FORMATS):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "write_subs":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "write_auto_subs":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "output":
            if not (
                isinstance(value, list)
                and all(
                    isinstance(item, str)
                    or (isinstance(item, str) and item in OUTPUT_TEMPLATE_VARIABLES)
                    for item in value
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "paths":
            if not (
                isinstance(value, dict)
                and all(
                    isinstance(k, str) and k in PATHS_KEYS and isinstance(v, str)
                    for k, v in value.items()
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "download_archive":
            if not (isinstance(value, str) or value is False):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "playlist_ids":
            if not (
                value == "ALL_ITEMS"
                or (
                    isinstance(value, list)
                    and all(isinstance(item, str) for item in value)
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "concurrent_fragments":
            if not isinstance(value, int):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "break_on_existing":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "windows_filenames":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "abort_on_unavailable_fragments":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "keep_fragments":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "batch_file":
            if not (isinstance(value, str) or value is False):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "force_overwrites":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "write_thumbnail":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "live_from_start":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "wait_for_video":
            if not (isinstance(value, int) or value is False):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "mark_watched":
            if not isinstance(value, bool):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "js_runtimes":
            if not (
                isinstance(value, dict)
                and all(
                    isinstance(k, str) and k in JS_RUNTIMES_KEYS and isinstance(v, str)
                    for k, v in value.items()
                )
            ):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "skip_playlist_after_errors":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "retries":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "file_access_retries":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "fragment_retries":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "extractor_retries":
            if not (isinstance(value, int) or value == "infinite"):
                print(f"Invalid value for key '{key}': {value}")
                return False
        elif key == "limit_rate":
            if not (isinstance(value, str) or value is False):
                print(f"Invalid value for key '{key}': {value}")
                return False

    return True


if __name__ == "__main__":
    # Ejemplo de uso
    options: VidraOptions = {
        "audio_language": "bestaudio",
        "video_resolution": "720",
        "ignore_errors": True,
        "use_extractors": ["youtube", "vimeo"],
        "wait_for_video": 30,
        "add_headers": {"User-Agent": "Mozilla/5.0"},
    }
    print(is_valid_options(options))  # Debería imprimir True
    invalid_options = {
        "audio_language": "invalid_option",
        "video_resolution": 720,
        "ignore_errors": "yes",
    }
    print(is_valid_options(invalid_options))  # Debería imprimir False
    str_assign_dict_to_vars = ""
    for key in VidraOptions.__annotations__.keys():
        str_assign_dict_to_vars += f'{key} = options["{key}"]\n'
    print(str_assign_dict_to_vars)
