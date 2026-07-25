# kids-english-tube

A hand-picked board of **English-speaking YouTube channels a child can watch alone**,
grouped by topic. Pick a topic, see every channel in it with its **10 newest videos** —
fetched live from YouTube on every page load. Video titles are auto-translated to
Vietnamese in the browser. UI is Vietnamese.

**Live page:** https://chungminhtu.github.io/kids-english-tube/

## How channels were picked

- **Spoken English only** — no Vietnamese / Korean / Chinese / Japanese-language channels,
  and no silent ones (ASMR, art timelapse, instrumental music, wordless process videos).
  They teach no listening.
- **Child-watchable and child-understandable**, judged from each channel's own About text —
  not its name. So no adult channels (medical animation, professional machining, adult ESL
  courses), no teacher/parent-facing channels, no prank, reaction or hype channels.
- Result: 10 topics, 56 channels. There is no "ask a parent first" tier — if a channel
  needed one, it was dropped.

## Nothing about videos is stored here

`channels.js` holds names, channel ids and a one-line Vietnamese description each. Titles,
thumbnails and dates come from YouTube's public RSS feed at page load; Vietnamese titles come
from a translation call in the browser. No API key, no login, no build step, no tracking.

Browsers can't read that feed directly (no CORS headers), so the page tries 6 public proxies
in turn. Feeds are cached in `localStorage` for 1 hour and translations are kept indefinitely,
so a reload costs no network calls. The chosen topic and search text survive a reload too.

## Run it locally (optional, faster)

```sh
python3 kids_yt.py           # http://127.0.0.1:8777
python3 kids_yt.py --lan     # also open it from a phone/iPad on the same wifi
python3 kids_yt.py --selftest
```

The page detects the local server and uses it instead of the public proxies, with a 6-hour
on-disk cache. Python 3 standard library only, no dependencies.

## Edit the list

`channels.js` is plain data: `"topic": [[name, channelId, "mô tả tiếng Việt"], …]`.
Add or remove a line and reload. The channel id is the `UC…` string in a channel URL.

MIT licensed. Channel names and thumbnails belong to their creators.
