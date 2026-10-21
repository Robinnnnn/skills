---
name: dj-set-ripper
description: Extract a tracklist from a DJ set or mix link and source the individual songs. Use for YouTube, SoundCloud, Mixcloud, 1001Tracklists, or a pasted tracklist; produce a per-track result log.
---

# DJ set ripper

Extract the set's tracklist, source its individual tracks, and preserve the result for every entry. Do not substitute one download of the full mix for the requested separate tracks.

## Tools

Use available web search/page tools for discovery, `yt-dlp` or `spotdl` for downloads, and FFmpeg and ffprobe for audio extraction and inspection. The filename helper needs Python 3. Inspect installed command help before relying on flags; install missing tools only within the requested environment and scope.

## Extract the tracklist

Use available page-fetch/search tools for the supplied URL's description and track metadata. For YouTube, `yt-dlp --dump-single-json "<url>"` can expose its description. Read the relevant description or structured tracklist, preserving its source URL. 1001Tracklists can be useful when the set page has no tracklist.

Parse a JSON array with `number`, `timestamp`, `artist`, and `title`. Preserve remix/mix names and meaningful artist spelling. Use `null` for missing timestamps. Keep unidentified `ID` entries and record uncertainty; skip timestamp-only lines. Never fill in unidentified music by guessing. If no tracks can be extracted, explain the result and request a pasted tracklist if needed.

Save this tracklist with the set's title and source URL in a dedicated output folder outside the skill repository. Derive a safe folder name or use the user's destination; metadata is text, not a shell command or path.

## Source individual tracks

Deduplicate identical artist/title/version requests while retaining all original tracklist positions. Leave unidentified tracks in the log. Match the exact artist, title, and remix; prefer an extended mix when no version is specified. A different original or radio edit is not an equivalent match.

Search Bandcamp, Beatport, Amazon's digital music store, Spotify metadata, then YouTube, stopping at a verified suitable match. Surface purchase links and observed prices for paid releases; do not buy tracks. In free-only mode, skip purchase searches and use available free or user-accessible sources. Report unavailable releases and region restrictions without silently substituting another version.

Download accessible audio as MP3 into the set folder, preserving existing files. Verify artist/title/version, duration, decoding, and output metadata. Preserve available tags and cover art; include BPM/key only when sourced. Record the source URL and measured format, bitrate, and size. Spotify supplies metadata to spotDL, not proof of the downloaded audio's provenance or quality; encoding at 320 kb/s cannot restore quality missing from the source. A valid file alone does not establish a correct musical match.

When workers are available, distribute distinct tracks in bounded batches of three to five. Collect their filenames, source URLs, measured bitrate/size, and status. Wait for all batches before normalizing filenames so workers do not rename each other's files.

Resolve bundled helper paths relative to this skill directory. Use the Python 3 helper to preview filenames against the verified `artist`/`title` tracklist:

```sh
python3 scripts/normalize_filenames.py /absolute/set-folder /absolute/tracklist.json
```

Inspect the plan, then repeat with `--apply`. The helper requires all verified artist/title words and allows only familiar extra downloader labels such as Official, Audio, Video, Lyrics, or HD. It skips extra remix, performer, version, or unknown words for manual review; preserve the exact remix in the tracklist. It also skips full mixes, occupied targets, ambiguous matches, and symlinks. The shell entrypoint `scripts/normalize-filenames.sh` accepts the same arguments.

## Optional full mix

Download the full mix only when the user requests it. Use a distinct name such as `Set Name [Full Mix].mp3`, and record its source and result separately.

## Result log

Write a timestamped log in the set folder with the original URL, extracted tracklist, and one result per entry. Include artist/title/version, source, status, filename or purchase link, and measured size/bitrate when a file exists. Distinguish downloaded, purchase available, not found, alternate version, and unidentified results. Explain meaningful failures such as an unavailable remix or region restriction. Summarize the totals without counting duplicate positions as extra downloads.

Keep downloaded audio, logs, and user tracklists outside this skill repository. Deliver links to actual files and the log, with unresolved entries visible.
