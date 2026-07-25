# kids-english-tube

A hand-picked board of **English-speaking YouTube channels for kids**, grouped by topic.
Open the page, everything is already expanded: every topic, every channel, and the
**5 newest videos** of each channel — fetched live from YouTube every time the page loads.

**Live page:** https://chungminhtu.github.io/kids-english-tube/

Interface is in Vietnamese (built for a Vietnamese family learning English).

## Why this list

Picked so that a child actually *hears English*:

- English spoken out loud — no Vietnamese / Korean / Chinese / Japanese-language channels.
- No silent channels: no ASMR, no art timelapse, no instrumental music, no wordless
  "manufacturing process" or silent build videos. They look nice and teach no listening.
- Two labels: **TỰ XEM** (fine on their own) and **XEM TRƯỚC** (a parent should watch first —
  ads, hype, pranks, power tools).

12 topics, 97 channels: kids' English, English practice, school subjects, animals & nature,
science & experiments, space, diving & fishing, camping, making & crafts, cooking,
family entertainment, gaming.

## No video data is stored here

The only data in this repo is `channels.js` — names, channel ids, labels. Video titles,
thumbnails and dates are pulled at page load from YouTube's public RSS feed
(`/feeds/videos.xml?channel_id=…`). No API key, no login, no build step, no tracking.

Browsers can't call that feed directly (no CORS headers), so the static page routes it
through a public CORS proxy, with two fallbacks if the first is down.

## Run it locally (optional, faster)

```sh
python3 kids_yt.py           # http://127.0.0.1:8777
python3 kids_yt.py --lan     # also open it from a phone/iPad on the same wifi
python3 kids_yt.py --selftest
```

The page detects the local server and uses it instead of the public proxy — same UI, plus a
6-hour on-disk cache. Python 3 standard library only, no dependencies.

## Edit the list

`channels.js` is plain data: `"topic": [[name, channelId, "OK" | "WATCH"], …]`.
Add or drop a line, reload the page. Channel id is the `UC…` string in a channel URL.

MIT licensed. Channel names and thumbnails belong to their creators.
