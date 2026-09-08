# Test patterns

- Construct typed parameters directly and assert invalid values fail closed.
- Generate the same request twice and compare canonical arrays/digests.
- Use `tmp_path` for real PNG, GIF, WAV, MP4, and manifest outputs.
- Skip ffmpeg-dependent tests only when the executable is genuinely absent.
- Test optional-backend failures with a real unavailable executable or a
  capability boundary, never with mocked media. Network-transport seams may be
  sealed at the module boundary (monkeypatching `urlopen`), but media and data
  stay real.

