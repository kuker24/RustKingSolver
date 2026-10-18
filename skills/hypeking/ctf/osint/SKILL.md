---
name: ctf-osint
description: "CTF OSINT checklist — EXIF GPS to map geolocation, date/time reconstruction from a person's timeline, retail/landmark-anchored geo chains, social account discovery, blockchain/ETH on-chain tracing, Wayback/archive, image reverse search. Trigger: osint, geolocation, geo-int, exif gps, where was this taken, find the person, social media account, blockchain osint, on-chain, wayback, reverse image search."
---

# CTF OSINT — checklist

CTV lost 3 of 18 here, all for the same reason: **the chain was abandoned before
a written hypothesis existed.** Every OSINT challenge is a *chain* — write each hop
down before taking it.

## 0. Split the chain into hops

```
artifact → location entity → landmark → district → city → country
person  → timeline → same-time activity → account → post → location
hash    → tx → address → entity label → owner
```

One hop per line. A hop with no evidence stays `UNKNOWN` — do not jump it.

## 1. EXIF GPS → map (cheapest win)

```bash
exiftool -a -G1 -n image.jpg | grep -Ei 'gps|date'
```

- `GPSLatitude/Ref`, `GPSLongitude/Ref`, `GPSPosition` → paste into a map, **then
  look at the satellite view** for the flag's theme (a building, a sign).
- No GPS? Check XMP, ICC, thumbnail, and the comment field.

## 2. Date/time reconstruction (the `pace` class)

Given "Tuesday 7 August 2018, afternoon, he was in **a** country", find the city.

- Pin the timezone from other artifacts (post timestamps, sunrise/sunset, weather).
- Cross-reference the person's *other* posts on that same day — the gap is the clue,
  not the noise.
- Sports/health-living personas (`pace`): check strava-like public activity, race
  calendars, and gym/event posts for that exact date.
- If the day is empty, the **absence** is the signal: they were moving.

## 3. Retail/landmark-anchored geo (the `bird-lovers` class)

Description gives relative bearings, not coordinates:

> "City of Electricity, east of the second-largest home-electronics retailer,
> ~300 m, 4–5 minutes on foot."

Method:
1. Resolve the **retail chain** from "second-largest in that country" → the brand.
2. Enumerate that brand's stores in the named city (the "City of Electricity" is a
   nickname — resolve it: e.g. a city known for power generation).
3. Apply the **bearing + distance** filter in Google Maps (measure tool).
4. Then resolve the *building* name and its known events.

Do not skip step 1 — the brand is the anchor that reduces the search space.

## 4. Social account discovery (the `wife-husband` class)

Flag format `REDLIMIT{sosmed.com/username}` — you need platform + handle.

- Search the person's **full name in quotes** plus each platform.
- Try handle variants: full name, initials, name+year, name+role (pilot), and the
  spouse's handle as a pivot (follows/mentions).
- Check **archives**: Wayback of the person's known pages, Google cache, and
  platform-specific mirrors.
- Cross-check identity with a second signal (photo, employer, location) before
  submitting — a same-name account is the classic wrong flag.

## 5. Blockchain (the `is-there-a-bitcoin` class)

- ETH address → explorer → transactions → counterparty addresses → **cluster into
  an entity label** (exchange, fund, whale).
- A 32-byte hex value is a **tx hash or a storage slot**, not a flag — look it up.
- Timestamp first: the genesis block time in CTV notes was `02:15:05Z`, not the
  assumed `03:54:39Z`. **Do not assume the block; find it.**

## 6. Toolbox

| Need | Tool |
|---|---|
| EXIF/GPS | `exiftool -a -G1 -n` |
| Reverse image | Google Lens, Yandex, Bing Visual |
| Maps | Google Maps measure, OSM, satellite + street view |
| Archives | Wayback Machine, `archive.today`, Google cache |
| Blockchain | Etherscan, Blockchair |
| Certificates | `crt.sh`, `censys` |


## 7. Global Intelligence Feeds & Telemetry (God's Eye View)

For multi-domain real-time monitoring, flight tracking (ADS-B), maritime tracking (AIS), orbital passes (TLE/CelesTrak), seismic events (USGS), and thermal fire/hotspot sensors (NASA FIRMS), consult:
- `references/gods-eye-view-sources.md`
## Delegation

Heavy research chains go to a **subagent per chain**, not inline. Give it the
description verbatim, the hop list, and the expected flag format. CTV ran
`SubBirdLovers`, `SubPace`, `SubWifeHusband` as separate agents for exactly this.

## Output contract

```
HOPS:     hop → evidence, hop → evidence, …
UNKNOWN:  <the hop with no evidence>
ANSWER:   <entity / account / place>
FLAG:     <flag>
```
