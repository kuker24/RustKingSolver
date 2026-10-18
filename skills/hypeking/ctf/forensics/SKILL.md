---
name: ctf-forensics
description: "CTF forensics checklist — zero-width steganography, pcap and partial-TLS reconstruction, large (>1GB) artifact workflow, audio/JPEG/PNG stego, metadata, disk images, ZWS block-aligned decoding. Trigger: forensics, stego, zero-width, zws, pcap, wireshark tls, hidden in metadata, audio forensics, image stego, disk image, memory dump."
---

# CTF forensics — checklist

Two failure modes dominate this category, and both hit in CTV:
**(a) the artifact was too big and never finished downloading**, **(b) the
encoding model was wrong and brute force ate the clock.**

## 0. Fetch first, analyse in parallel

Never inline a multi-GB download.

```bash
python3 ~/.omp/agent/skills/hypeking/ctf/scripts/fetch-artifact.py '<url>' -o work/<slug>/ &
# keep working on local artifacts while it runs; poll size, do not block
```

`artifact` (2.99 GB Drive, CTV) failed purely on this. Start the transfer in the
background **before** reading the description twice.

## 1. Classify in 60 seconds

```bash
file * ; exiftool * | head -40 ; binwalk -e * ; du -h *
```

| Signal | Path |
|---|---|
| `text/plain` with oddly missing/odd spacing | **zero-width** (§2) |
| `.pcap/.pcapng` | §3 |
| `.jpg/.png/.wav/.mp3` | §4 |
| image with GPS in EXIF | hand off to `../osint/` |
| `PNG` with a weird size / `IHDR` mismatch | §4 |
| archive inside archive | `binwalk -e` then recurse |

## 2. Zero-width steganography (the `seen-it` class)

Text where nothing looks wrong but the byte count exceeds the visible characters.
U+200B/200C/200D/FEFF/2060 encode bits.

**The model that works: block-aligned, per visible character.**

1. Split the stream into runs delimited by visible characters.
2. If **every run has the same length**, that length is the bits-per-char — do **not**
   require global divisibility (that test is what made CTV loop).
3. Decode each run independently → one symbol per visible char.
4. Score by printable-ASCII + expected prefix, not by raw bit count.

**Bug to avoid:** iterating a `bytes` object yields `int`s, not 1-char strings — the
scoring silently returns garbage. Decode to `str` first.

Try bases 2, 3 (base-8 chunking) and 8 systematically. If the per-char block length
varies, the delimiter *is* the signal — treat separator choice as a bit too.

## 3. pcap / network

```bash
tshark -r a.pcap -q -z io,phs
tshark -r a.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

- **Partial TLS decryption** (the `is-there-a-bitcoin` class): the capture has a
  readable request line and a partly-decrypted response. Reconstruct the *API call*:
  host + path + params tell you what was queried, even when the body is redacted.
- Then replay the query against the public API/explorer to recover the redacted
  entity. Redaction is not encryption.
- Look for: DNS, SNI, certificate CN, `Referer`, and the response `Content-Length`
  (length is a fingerprint even when content is gone).

## 4. Image / audio

- `exiftool -a -G1` first — comment, XMP, ICC, GPS, `Software`.
- PNG: check for extra chunks (`pngcheck -v`); a `tEXt`/`zTXt` chunk is common.
- LSB: try planes in order 0,1,2 and both bit orders; **validate against a known
  prefix**, never eyeball.
- Audio (`the-audio-incident`): check spectrogram, DTMF, SSTV, morse, and LSB of the
  PCM stream. Generate the spectrogram image and *look* at it.
- JPEG (`stecrac`, `sterafi`): `steghide`, `outguess`, `jsteg`, DCT coefficient
  manipulation; try empty passphrases first.

## 5. Metadata / document

`exiftool`, `pdfinfo`, `pdf-parser`, `xxd` on the tail. `hidden-in-metadata`-class
flags live in author, comment, or an appended blob after EOF.

## Output contract

```
CLASS:    zws | pcap | image | audio | metadata | archive
MODEL:    <bit grouping / key / passphrase used>
FLAG:     <flag>
NEGATIVE: <what you ruled out, with the probe>
```
