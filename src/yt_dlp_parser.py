from typing import (
    List,
    cast,
    Final,
)

from yt_dlp_parser_types import (
    VidraOptions,
    OUTPUT_TEMPLATE_VARIABLES,
)

DEFAULT_OPTIONS: Final[VidraOptions] = {
    "audio": "default",
    "video": "default",
    "subtitles": "default",
    "ignore_errors": False,  # True=Ignorar errores, no lanzar excepción
    "abort_on_error": False,  # False=Si se lanza excepción, esta es ignorada
    "use_extractors": ["default"],
    "flat_playlist": False,
    "live_from_start": True,
    "wait_for_video": False,
    "mark_watched": False,
    "proxy": "",
    "socket_timeout": "infinite",
    "source_address": "",
    "impersonate": "",
    "force_ipv4": False,
    "force_ipv6": False,
    "enable_file_urls": False,
    "geo_verification_proxy": "",
    "xff": "",
    "prefer_insecure": False,
    "add_headers": {},
    "cookies": "",
    "cookies_from_browser": False,
    "username": "",
    "password": "",
    "twofactor": "",
    "video_password": "",
    "video_multistreams": True,
    "audio_multistreams": True,
    "merge_output_format": "mkv",
    "audio_format": "best",
    "extract_audio": False,
    "audio_quality": 0,
    "remux_video": False,
    "embed_subs": True,
    "embed_thumbnail": True,
    "embed_metadata": True,
    "embed_chapters": True,
    "embed_info_json": True,
    "format": "",
    "xattrs": False,
    "fixup": "force",
    "ffmpeg_location": "",
    "convert_thumbnails": "webp",
    "write_subs": False,
    "write_auto_subs": False,
    "sub_format": "srt",
    "sub_langs": [],
    "output": ["title", "-", "id", ".", "ext"],
    "paths": {},
    "download_archive": False,
    "playlist": False,
    "playlist_items": "all",
    "concurrent_fragments": 1,
    "break_on_existing": False,
    "skip_playlist_after_errors": "infinite",
    "retries": 10,
    "file_access_retries": 3,
    "fragment_retries": 10,
    "abort_on_unavailable_fragments": False,
    "keep_fragments": False,
    "batch_file": False,
    "force_overwrites": True,
    "write_thumbnail": False,
    "sponsorblock_mark": [],
    "sponsorblock_remove": [],
    "extractor_retries": 3,
    "limit_rate": False,
    "windows_filenames": True,
}


def options_parser(options: VidraOptions) -> List[str]:
    # set default values for missing options
    for key, value in DEFAULT_OPTIONS.items():
        options.setdefault(key, value)  # type: ignore
    assert (
        "audio" in options
        and "video" in options
        and "subtitles" in options
        and "ignore_errors" in options
        and "abort_on_error" in options
        and "use_extractors" in options
        and "flat_playlist" in options
        and "live_from_start" in options
        and "wait_for_video" in options
        and "mark_watched" in options
        and "proxy" in options
        and "socket_timeout" in options
        and "source_address" in options
        and "impersonate" in options
        and "force_ipv4" in options
        and "force_ipv6" in options
        and "enable_file_urls" in options
        and "geo_verification_proxy" in options
        and "xff" in options
        and "prefer_insecure" in options
        and "add_headers" in options
        and "cookies" in options
        and "cookies_from_browser" in options
        and "username" in options
        and "password" in options
        and "twofactor" in options
        and "video_password" in options
        and "video_multistreams" in options
        and "audio_multistreams" in options
        and "merge_output_format" in options
        and "audio_format" in options
        and "extract_audio" in options
        and "audio_quality" in options
        and "remux_video" in options
        and "embed_subs" in options
        and "embed_thumbnail" in options
        and "embed_metadata" in options
        and "embed_chapters" in options
        and "embed_info_json" in options
        and "format" in options
        and "xattrs" in options
        and "fixup" in options
        and "ffmpeg_location" in options
        and "convert_thumbnails" in options
        and "write_subs" in options
        and "write_auto_subs" in options
        and "sub_format" in options
        and "sub_langs" in options
        and "output" in options
        and "paths" in options
        and "download_archive" in options
        and "playlist" in options
        and "playlist_items" in options
        and "concurrent_fragments" in options
        and "break_on_existing" in options
        and "skip_playlist_after_errors" in options
        and "retries" in options
        and "file_access_retries" in options
        and "fragment_retries" in options
        and "abort_on_unavailable_fragments" in options
        and "keep_fragments" in options
        and "batch_file" in options
        and "force_overwrites" in options
        and "write_thumbnail" in options
        and "sponsorblock_mark" in options
        and "sponsorblock_remove" in options
        and "extractor_retries" in options
        and "limit_rate" in options
        and "windows_filenames" in options
    ), "Missing required options"
    audio = options["audio"]
    video = options["video"]
    subtitles = options["subtitles"]
    ignore_errors = options["ignore_errors"]
    abort_on_error = options["abort_on_error"]
    use_extractors = options["use_extractors"]
    flat_playlist = options["flat_playlist"]
    live_from_start = options["live_from_start"]
    wait_for_video = options["wait_for_video"]
    mark_watched = options["mark_watched"]
    proxy = options["proxy"]
    socket_timeout = options["socket_timeout"]
    source_address = options["source_address"]
    impersonate = options["impersonate"]
    force_ipv4 = options["force_ipv4"]
    force_ipv6 = options["force_ipv6"]
    enable_file_urls = options["enable_file_urls"]
    geo_verification_proxy = options["geo_verification_proxy"]
    xff = options["xff"]
    prefer_insecure = options["prefer_insecure"]
    add_headers = options["add_headers"]
    cookies = options["cookies"]
    cookies_from_browser = options["cookies_from_browser"]
    username = options["username"]
    password = options["password"]
    twofactor = options["twofactor"]
    video_password = options["video_password"]
    video_multistreams = options["video_multistreams"]
    audio_multistreams = options["audio_multistreams"]
    merge_output_format = options["merge_output_format"]
    audio_format = options["audio_format"]
    extract_audio = options["extract_audio"]
    audio_quality = options["audio_quality"]
    remux_video = options["remux_video"]
    embed_subs = options["embed_subs"]
    embed_thumbnail = options["embed_thumbnail"]
    embed_metadata = options["embed_metadata"]
    embed_chapters = options["embed_chapters"]
    embed_info_json = options["embed_info_json"]
    format = options["format"]
    xattrs = options["xattrs"]
    fixup = options["fixup"]
    ffmpeg_location = options["ffmpeg_location"]
    convert_thumbnails = options["convert_thumbnails"]
    write_subs = options["write_subs"]
    write_auto_subs = options["write_auto_subs"]
    sub_format = options["sub_format"]
    sub_langs = options["sub_langs"]
    output = options["output"]
    paths = options["paths"]
    download_archive = options["download_archive"]
    playlist = options["playlist"]
    playlist_items = options["playlist_items"]
    concurrent_fragments = options["concurrent_fragments"]
    break_on_existing = options["break_on_existing"]
    skip_playlist_after_errors = options["skip_playlist_after_errors"]
    retries = options["retries"]
    file_access_retries = options["file_access_retries"]
    fragment_retries = options["fragment_retries"]
    abort_on_unavailable_fragments = options["abort_on_unavailable_fragments"]
    keep_fragments = options["keep_fragments"]
    batch_file = options["batch_file"]
    force_overwrites = options["force_overwrites"]
    write_thumbnail = options["write_thumbnail"]
    sponsorblock_mark = options["sponsorblock_mark"]
    sponsorblock_remove = options["sponsorblock_remove"]
    extractor_retries = options["extractor_retries"]
    limit_rate = options["limit_rate"]
    windows_filenames = options["windows_filenames"]

    comando = ["./yt-dlp"]
    # format = [["bestvideo", "bestaudio"],["bestvideo"]] -> bestvideo+bestaudio/bestvideo
    if isinstance(format, list):
        format = "/".join(
            [
                f if isinstance(f, str) else "+".join([a for a in f if a.strip()])
                for f in format
                if f
            ]
        )
    elif format is None:
        format = ""

    format = cast(str, format)
    format = [f.split("+") for f in format.split("/") if f.strip()]
    format = format if format else cast(List[List[str]], [])

    def parse_video(video: str):
        if video == "bestvideo":
            return "bestvideo"
        return f"bestvideo[height<={video}]"

    def parse_audio(audio: str):
        if audio == "bestaudio":
            return "bestaudio"
        return f"bestaudio[language^={audio}]"

    if video != "default":
        format.insert(
            0, [parse_audio(audio) if audio else "bestaudio", parse_video(video)]
        )
    elif audio != "default":
        format.insert(0, [parse_audio(audio)])
    format.append(["bestvideo", "bestaudio"])

    if subtitles == "default":
        pass
    elif subtitles == "all":
        sub_langs.insert(0, "all")
    elif subtitles == "none":
        sub_langs = []
    else:
        sub_langs.insert(0, subtitles)

    if extract_audio:
        format = [["bestaudio"], ["best"]]
        sub_langs = []
        embed_subs = False
        write_subs = False
        write_auto_subs = False
    # General Options
    if ignore_errors:
        comando.append("--ignore-errors")
    if abort_on_error:
        comando.append("--abort-on-error")
    else:
        comando.append("--no-abort-on-error")
    if use_extractors:
        comando.extend(["--use-extractors", ",".join(use_extractors)])
    if flat_playlist:
        comando.append("--flat-playlist")
    else:
        comando.append("--no-flat-playlist")
    if live_from_start:
        comando.append("--live-from-start")
    else:
        comando.append("--no-live-from-start")
    if wait_for_video is False:
        comando.append("--no-wait-for-video")
    else:
        comando.extend(["--wait-for-video", str(wait_for_video)])
    if mark_watched:
        comando.append("--mark-watched")
    else:
        comando.append("--no-mark-watched")
    # Network Options
    if proxy:
        comando.extend(["--proxy", proxy])
    if socket_timeout != "infinite":
        comando.extend(["--socket-timeout", str(socket_timeout)])
    if source_address:
        comando.extend(["--source-address", source_address])
    if impersonate:
        comando.extend(["--impersonate", impersonate])
    if force_ipv4:
        comando.append("--force-ipv4")
    if force_ipv6:
        comando.append("--force-ipv6")
    if enable_file_urls:
        comando.append("--enable-file-urls")
    # Geo-restriction
    if geo_verification_proxy:
        comando.extend(["--geo-verification-proxy", geo_verification_proxy])
    if xff:
        comando.extend(["--xff", xff])
    # Video Selection
    if playlist_items == "all":
        # Por defecto yt-dlp descarga toda la playlist.
        pass
    elif isinstance(playlist_items, list):
        items_str = ",".join(map(str, playlist_items))
        comando.extend(["--playlist-items", items_str])
    if playlist:
        comando.append("--yes-playlist")
    else:
        comando.append("--no-playlist")
    if download_archive:
        comando.extend(["--download-archive", download_archive])
    if break_on_existing:
        comando.append("--break-on-existing")
    else:
        comando.append("--no-break-on-existing")
    if skip_playlist_after_errors != "infinite":
        comando.extend(
            ["--skip-playlist-after-errors", str(skip_playlist_after_errors)]
        )
    # Download Options
    if concurrent_fragments:
        comando.extend(["--concurrent-fragments", str(concurrent_fragments)])
    if limit_rate:
        comando.extend(["--limit-rate", limit_rate])
    comando.extend(["--retries", str(retries)])
    comando.extend(["--file-access-retries", str(file_access_retries)])
    comando.extend(["--fragment-retries", str(fragment_retries)])
    if abort_on_unavailable_fragments:
        comando.append("--abort-on-unavailable-fragments")
    else:
        comando.append("--skip-unavailable-fragments")
    if keep_fragments:
        comando.append("--keep-fragments")
    # Filesystem Options
    if batch_file is False:
        comando.append("--no-batch-file")
    elif batch_file:
        comando.extend(["--batch-file", batch_file])
    if paths:
        for k, v in paths.items():
            comando.extend(["-P", f"{k}:{v}"])
    if isinstance(output, str) and output:
        comando.extend(["--output", output])
    elif isinstance(output, list):
        nombre = ""
        for i in output:
            if i in OUTPUT_TEMPLATE_VARIABLES:
                nombre += f"%({i})s"
            else:
                nombre += i
        comando.extend(["--output", nombre])
    if force_overwrites:
        comando.append("--force-overwrites")
    else:
        comando.append("--no-force-overwrites")
    if cookies is False:
        comando.append("--no-cookies")
    elif cookies:
        comando.extend(["--cookies", cookies])
    if cookies_from_browser is False:
        comando.append("--no-cookies-from-browser")
    elif cookies_from_browser:
        comando.extend(["--cookies-from-browser", cookies_from_browser])
    # Thumbnail Options
    if write_thumbnail:
        comando.append("--write-thumbnail")
    else:
        comando.append("--no-write-thumbnail")
    # Workarounds
    if prefer_insecure:
        comando.append("--prefer-insecure")
    for header_key, header_value in add_headers.items():
        comando.extend(["--add-headers", f"{header_key}: {header_value}"])
    # Video Format Options
    if format:
        # fix and normalize format string
        format = "/".join(["+".join(set(f)) for f in format])
        comando.extend(["--format", format])
    if video_multistreams:
        comando.append("--video-multistreams")
    if audio_multistreams:
        comando.append("--audio-multistreams")
    if merge_output_format:
        comando.extend(["--merge-output-format", merge_output_format])
    # Subtitle Options
    if write_subs:
        comando.append("--write-subs")
    else:
        comando.append("--no-write-subs")
    if write_auto_subs:
        comando.append("--write-auto-subs")
    else:
        comando.append("--no-write-auto-subs")
    if sub_format:
        comando.extend(["--sub-format", sub_format])
    if sub_langs:
        comando.extend(["--sub-langs", ",".join(sub_langs)])
    # Authentication Options
    if username:
        comando.extend(["--username", username])
    if password:
        comando.extend(["--password", password])
    if twofactor:
        comando.extend(["--twofactor", twofactor])
    if video_password:
        comando.extend(["--video-password", video_password])
    # Post-processing Options
    if extract_audio:
        comando.append("--extract-audio")
    if audio_format:
        comando.extend(["--audio-format", audio_format])
    if audio_quality is not None:
        comando.extend(["--audio-quality", str(audio_quality)])
    if remux_video:
        comando.extend(["--remux-video", remux_video])
    if embed_subs:
        comando.append("--embed-subs")
    if embed_thumbnail:
        comando.append("--embed-thumbnail")
    if embed_metadata:
        comando.append("--embed-metadata")
    if embed_chapters:
        comando.append("--embed-chapters")
    if embed_info_json:
        comando.append("--embed-info-json")
    if xattrs:
        comando.append("--xattrs")
    if fixup:
        comando.extend(["--fixup", fixup])
    if ffmpeg_location:
        comando.extend(["--ffmpeg-location", ffmpeg_location])
    if convert_thumbnails:
        comando.extend(["--convert-thumbnails", convert_thumbnails])
    # SponsorBlock Options
    if sponsorblock_mark:
        adds = [str(item) for item in sponsorblock_mark if item]
        if adds:
            comando.extend(["--sponsorblock-mark", ",".join(adds)])
    if sponsorblock_remove:
        removals = [str(item) for item in sponsorblock_remove if item]
        if removals:
            comando.extend(["--sponsorblock-remove", ",".join(removals)])
    # Extractor Options
    if extractor_retries is not None:
        comando.extend(["--extractor-retries", str(extractor_retries)])
    if windows_filenames:
        comando.append("--windows-filenames")
    for part in comando:
        if isinstance(part, (list, tuple, set)):
            raise ValueError(f"Invalid command part: {part}")
    return comando
