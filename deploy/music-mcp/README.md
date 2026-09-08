# BOX V2 NetEase Music MCP

The firmware reuses queued Ogg Opus playback from `D:\wumingxiaozhi`.
The existing private gateway and MCP server on `aliyun_ecs` are reused.

## Firmware

Board directory: `waveshare/esp32-s3-touch-lcd-1.85c`.
Music variant: `esp32-s3-touch-lcd-1.85c-box-v2-music`.
The base board type and V2 pins are unchanged; the custom firmware name is
distinct from the stock release name.

In the ESP-IDF 6.0.2 terminal, from the project root:

```powershell
python scripts/build.py waveshare/esp32-s3-touch-lcd-1.85c --name esp32-s3-touch-lcd-1.85c-box-v2-music --language zh-CN
```

Device tools:

- `self.music.play_url(audio_url, title, artist)` accepts only signed URLs
  under `http://47.108.114.17:8081/xiaozhi-music/audio_ogg/`.
- `self.music.stop()` stops playback and clears the pending request.
- Playback waits for the current spoken response to drain. A new song replaces
  the previous song/request, and the display shows its title and artist.
- The stock variant does not register these tools.

The MCP endpoint token and the NetEase account cookie are never compiled into
the firmware. Keep the custom variant when rebuilding or installing updates;
stock firmware does not contain the music tools.

## Cloud Instance

The new instance is `xiaozhi-music-mcp@agent_2323485.service`, enabled at boot.
It uses the existing `/etc/systemd/system/xiaozhi-music-mcp@.service` template.

| Purpose | Server location |
| --- | --- |
| Endpoint configuration | `/etc/xiaozhi-music-mcp-agent_2323485.env`, root-only mode 0600 |
| Shared gateway credentials | `/etc/xiaozhi-music.env` |
| MCP bridge | `/opt/xiaozhi-music-mcp/mcp_pipe.py` |
| Search tool | `/opt/xiaozhi-music-mcp/music_mcp.py` |
| Gateway | `/opt/xiaozhi-music/music_gateway.py`, port 3060 |

The supplied endpoint is saved locally in `.env`, ignored by Git. `.env.example`
contains placeholders only. Existing `legacy` and `agent_2309363` instances are
left running. No shared gateway source, account cookie, or service was replaced.

```powershell
ssh aliyun_ecs 'systemctl status xiaozhi-music-mcp@agent_2323485.service --no-pager'
ssh aliyun_ecs 'journalctl -u xiaozhi-music-mcp@agent_2323485.service -n 30 --no-pager'
Get-Content deploy/music-mcp/verify_service.py -Raw | ssh aliyun_ecs /opt/xiaozhi-music-mcp/venv/bin/python -
```

Verification on 2026-09-07: the endpoint connected, the cloud requested its
tool list and sent heartbeats, and a real MCP search returned an exact title
and a valid `audio/ogg` stream (8192 bytes checked, `OggS` header present).
At initial deployment the gateway used exact title/artist matching. Unavailable tracks return
a failure instead of substituting a different song.

The existing 67 host tests passed under WSL. Native Windows runs encounter five
temporary-directory cleanup errors in upstream tests. Firmware build and device
flash/startup evidence are recorded separately under `logs/`.

BOX V2 music firmware built and flashed to COM11 successfully. All five flash
images passed write verification. The application is 2,812,128 bytes with 32%
of its OTA slot free. Startup reported the custom SKU, both music tools, a
successful Wi-Fi/MQTT connection, and the `idle` state. Physical music playback,
voice interruption, stop, and reconnect recovery still require a device trial.

- Build: `logs/build_music_COM11.log`
- Flash: `logs/flash_music_COM11.log`
- Cloud search/audio check: `logs/music_service_verification.log`
- Serial startup: `logs/COM11_music_20260907_111306.log`
- Active serial monitor PID and log: `logs/COM11_monitor.json`

## Search Fix, 2026-09-07

The cloud search fix is live on `aliyun_ecs`. Source is maintained in
`D:/xiaozhi_music_mcp/server/`. Artist matching now uses resolved IDs;
G.E.M.'s verified name aliases resolve to ID `7763`. Exact-title matching is
retained. Artist-only searches return ten works and require a second lookup
to obtain a verified playback URL. Distinct errors now identify missing
tracks, unavailable playback, ambiguous artists, provider failures, and rate
limits. Provider search/catalog caching and bounded rate-limit retry are enabled.

19 tests passed. Real MCP calls for Superpower with the plain Chinese singer
name, the canonical name, and a combined natural-language query all returned
track `1833633769`; artist-only listing and an 8192-byte Ogg stream also passed.
The previous Hu Da Qiang search/audio regression passed. The current agent MCP
instance was restarted and requested a fresh tool list. Firmware was not flashed.

Backup: `/opt/xiaozhi-music-search-fix-20260907/backup-20260907-133708`.
Evidence: `logs/music_search_fix_staging_20260907.log`,
`logs/music_search_fix_live_20260907.log`,
`logs/music_search_fix_regression_20260907.log`.
