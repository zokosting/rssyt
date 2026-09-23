def _download_once(folder, video_id, lang=None, pubdate="upload"):
    """Realiza un único intento de descarga. Puede lanzar DownloadError."""
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": str(folder / "%(id)s.%(ext)s"),
        "writethumbnail": True,
        "postprocessors": [{"key": "FFmpegThumbnailsConvertor", "format": "jpg"}],
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        # Componente remoto para resolver desafíos JS de YouTube
        "remote_components": ["ejs:github"],
        # Runtime de JavaScript (Deno) para resolver los challenges
        "js_runtimes": ["deno"],
    }
    # Usar cookies si se ha proporcionado un archivo a través de la variable de entorno
    cookie_file = os.environ.get("YTDLP_COOKIES_FILE")
    if cookie_file:
        opts["cookiefile"] = cookie_file

    # El cliente mweb es el que mejor funciona con PO Tokens para audio
    extractor_args = {"youtube": {"player_client": ["mweb"]}}
    if lang:
        extractor_args["youtube"]["lang"] = [lang]
    opts["extractor_args"] = extractor_args

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)

    filepath = Path(info["requested_downloads"][0]["filepath"])
    thumbnail = folder / f"{video_id}.jpg"
    timestamp = None
    if pubdate == "upload":
        timestamp = info.get("timestamp")
        if not timestamp and info.get("upload_date"):
            timestamp = int(
                datetime.strptime(info["upload_date"], "%Y%m%d")
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )
    return {
        "id": video_id,
        "title": info.get("title") or video_id,
        "description": info.get("description") or "",
        "timestamp": timestamp or int(datetime.now(timezone.utc).timestamp()),
        "duration": info.get("duration"),
        "link": info.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
        "file": filepath.name,
        "mime": MIME_TYPES.get(filepath.suffix.lstrip("."), "application/octet-stream"),
        "filesize": filepath.stat().st_size,
        "thumbnail": thumbnail.name if thumbnail.exists() else None,
    }