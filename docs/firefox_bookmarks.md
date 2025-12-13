# EQ12 Firefox Bookmarks

Place your bookmarks in `C:\EQ12\configs\bookmarks.json` as a list of objects with `title` and `url` fields.

Windows (PowerShell):

```
PowerShell\> .\scripts\eq12_firefox_bookmarks.ps1 -Apply
```

Cross-platform (Codespaces / Linux / macOS):

```
$ python3 scripts/eq12_firefox_bookmarks.py --apply --profile /workspaces/eq12/profiles/firefox-bot
```

Notes:
- Scripts are dry-run by default; pass `-Apply` (PowerShell) or `--apply` (Python) to perform writes.
- The tools write a simple `bookmarks_auto.html` that Firefox can import or open as a local file.
- For robust integration with Firefox's `places.sqlite` consider using `sqlite3` to manipulate `places` and `moz_bookmarks` tables; this repo prefers a conservative approach.
