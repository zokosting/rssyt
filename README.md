# youtubecast

Turns YouTube channels/playlists into audio podcast feeds. Runs from cron,
downloads audio + thumbnails with yt-dlp, generates `channel.xml` (podcast RSS)
per source. Point a static webserver at the `root` folder and subscribe to
`<base_url>/<folder>/channel.xml`.

## Requirements

Python 3.11+:

```sh
sudo apt install python3-venv ffmpeg
python3 -m venv venv
venv/bin/pip install yt-dlp
```

Python < 3.11 additionally needs `tomli` (a backport of stdlib `tomllib`):

```sh
venv/bin/pip install tomli
```

## Configuration

Copy `config.example.toml` to `config.toml` next to the script and edit:

```toml
base_url = "https://podcasts.example.com/"
root     = "/home/youtubecast/podcasts"
backlog  = 1

[[podcasts]]
url    = "https://www.youtube.com/@SomeChannel"
title  = "Some Channel"
folder = "some-channel"

[[podcasts]]
url           = "https://www.youtube.com/playlist?list=PL0123456789abcdef0123456789abcdef"
title         = "Some Playlist"
folder        = "some-playlist"
backlog       = 3
backlog_order = "asc"
pubdate       = "download"
```

- `base_url` — public URL the webserver serves `root` at
- `root` — folder where podcast folders are created (webserver docroot)
- `backlog` — how many latest videos to download when a source is added (default 1)
- `[[podcasts]]` — one per source: `url` (channel or playlist), `title` (podcast
  name), `folder` (folder name under `root`)

Optional, global or per-podcast (per-podcast wins):

- `backlog` — per-source override
- `backlog_order` — how the source lists its videos, used to pick the newest
  `backlog` videos on first run: `"desc"` (default) means newest first, so they
  are taken from the beginning; `"asc"` means oldest first, taken from the end.
  Channels always list newest first; playlists depend on their sort order
- `lang` — episode metadata is fetched in the video's original language by
  default; set e.g. `lang = "ru"` to pin a language if YouTube ever starts
  serving auto-translated titles/descriptions
- `pubdate` — what becomes the episode's pubDate: `"upload"` (default) uses the
  video's original upload date; `"download"` uses the time the episode was
  downloaded, so old videos added to a playlist appear as new episodes

## File structure

```
youtubecast/
├── youtubecast.py
├── config.toml
├── venv/
├── youtubecast.lock    # prevents overlapping cron runs
├── cron.log
└── podcasts/           # `root` from config, serve this with a webserver
    ├── some-channel_logo.jpg   # put it here yourself, the feed references it
    ├── some-channel/
    │   ├── channel.xml     # podcast RSS feed
    │   ├── episodes.json   # episode metadata, channel.xml is rebuilt from it
    │   ├── seen.txt        # video IDs already handled
    │   ├── <video_id>.m4a  # episode audio
    │   └── <video_id>.jpg  # episode thumbnail
    ├── some-playlist_logo.jpg
    └── some-playlist/
        └── ...
```

New videos are detected as "not in `seen.txt`", i.e. new since last *download*,
not last check — a failed download retries on the next run. Delete an ID from
`seen.txt` (and its files) to re-download it.

## Cron

`crontab -e`:

```cron
# check sources hourly
0 * * * *  cd /path/to/youtubecast && ./venv/bin/python youtubecast.py >> cron.log 2>&1
# update yt-dlp weekly (Mon 05:15) — yt-dlp is a pip package inside the
# project venv, so pip upgrades it in place
15 5 * * 1 /path/to/youtubecast/venv/bin/pip install -q --upgrade yt-dlp >> /path/to/youtubecast/cron.log 2>&1
```
