# Laoyuanxiaozhi private OTA

Reuses the Alibaba Cloud service implemented in `D:\wumingxiaozhi` at
`https://47.108.114.17:9443/xiaozhi-ota/`. The copied service sources are a
reference for that shared installation; adding this board requires publishing
its own release, not replacing the running service or the xiaozhou manifests.
Only the public root CA is included. Private keys remain on the server.

The API accepts a system-information POST at `api/v1/check?channel=test` and
selects `data/manifests/laoyuanxiaozhi/test.json` by `board.name`.
Files live under `data/files/laoyuanxiaozhi/<version>/`.
Official activation, server time, MQTT and WebSocket discovery remain separate.

## Publish after build and USB migration preparation

```powershell
.\scripts\publish_ota.ps1 -Version 2.4.2 -Channel test
```

The script checks CMake board identity and the raw application's embedded version,
uploads application/assets over SSH to a unique staging directory, and runs the
existing atomic publisher. It refuses replacement of different bytes at an
already published version. Increase the root CMakeLists.txt PROJECT_VER for the
next firmware release. Never upload merged-binary.bin as xiaozhi.bin.

Restart the device to check for a new release. Application and assets are separate
partitions; resources are scheduled for a subsequent boot. After physical test,
use the same files with `-Channel stable`. Stable promotion does not change a
device configured for test; its channel is selected by the build configuration.
Keep the previous release. Do not erase NVS or update the partition table through OTA.

The server reports size and SHA-256 metadata. The inherited firmware path uses
HTTPS and ESP image validation; it does not independently compare the manifest's
SHA-256. Assets updates are not dual-slot and must not be interrupted.

## Local checks

```powershell
python -m unittest discover -s deploy/ota-server -v
python -m unittest discover -s scripts/tests -v
python3 scripts/verify_private_ota.py --version 2.4.2
```

Publisher tests require Linux (`fcntl.flock`). Release 2.4.2 was published to
laoyuanxiaozhi/test on 2026-09-08. HTTPS downloads matched the manifest and local
application/assets SHA-256 values. COM11 subsequently completed USB migration and application/assets OTA to 2.4.3
(test channel), booted ota_1, marked the image valid, and reconnected to MQTT/idle.
Visual/audio acceptance remains separate; see docs/laoyuanxiaozhi-validation.md.

The existing server certificate lacks an Authority Key Identifier and Python 3.13
strict X.509 defaults reject it. The HTTPS health check passed using Ubuntu curl with the supplied CA and
chain/hostname verification enabled. Ubuntu Python also verified both release
downloads with the supplied CA. Do not use
an unverified SSL context. A future certificate renewal should include AKI/SKI
for compatibility with newer strict clients.

The current publisher assigns the requested release number to both firmware and
assets even when asset bytes are unchanged. Consequently 2.4.3 caused a second,
unnecessary assets download after application OTA. The device completed both;
this was not an application retry. Avoid claiming that this publisher automatically
reuses unchanged assets versions.
