# Encoding profiles and backend capabilities

| Format | Backend | Artifact | Profile | Status |
| --- | --- | --- | --- | --- |
| PNG | Pillow | image | lossless uint8 raster | available |
| WAV | python wave | audio | PCM 8/16/24/32-bit | available |
| GIF | Pillow | video | palette animation with declared duration | available |
| NPZ | NumPy | canonical artifact | exact little-endian float32 archive | available |
| MP4 | ffmpeg | video/audiovisual | H.264 or muxed MP4; decode inspected | available |

: Backend status is environment-dependent; encoded files are inspected after delivery. {#tbl:encodings}
