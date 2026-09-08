# laoyuanxiaozhi

独立 OTA 板型，硬件为 Waveshare ESP32-S3-Touch-LCD-1.85C-BOX V2。
类型与发布名称均为 `laoyuanxiaozhi`。复用原 BOX V2 源文件和引脚，
仅编译本目录包装源文件，包含一个 `DECLARE_BOARD` 工厂。
默认保留云音乐 MCP、360×360 人像表情、ES8311/ES7210 音频及 Wi-Fi。
沿用项目默认 16 MB Flash、`partitions/v2/16m.csv` 双应用分区和 8 MB assets。

## 构建

ESP-IDF 6.0.2 环境：

```powershell
python scripts/build.py laoyuanxiaozhi --name laoyuanxiaozhi --language zh-CN
```

本机也可执行 `scripts/build-laoyuanxiaozhi.cmd`，会更新 sdkconfig 和 build。
首次从旧 BOX V2 身份迁移通过 USB 刷入本板型固件及匹配资源，
沿用原分区布局并保留 NVS，不使用 erase-flash。

## OTA

- 官方接口负责激活、时间和 MQTT/WebSocket 连接配置。
- 私有接口为 `https://47.108.114.17:9443/xiaozhi-ota/api/v1/check?channel=test`。
- 内置 `deploy/ota-server/ota-root-ca.pem` 公共 CA，保持 TLS 校验。
- 私有 OTA 启用时忽略官方固件更新；私有服务不可用不阻止正常连接。
- 开机检查版本，先更新应用，再于后续启动检查并安装资源。
- 资源失败保留待更新记录，后续自然启动重试，避免连续重启。
- 发布使用 `scripts/publish_ota.ps1`，默认板型为 `laoyuanxiaozhi`，默认 test 通道。
- 不使用无名/xiaozhou 设备的固件或资源。新版本必须递增。
- 应用 OTA 不更新分区表、bootloader 或云端角色设定。

服务端说明见 `deploy/ota-server/README.md`。
角色设定稿见 `prompts/laoyuanxiaozhi-persona.md`，需单独配置到云端。

## 验收

USB 迁移后验证私有 HTTPS 检查、双 OTA 槽切换、重启确认、资源更新、
Wi-Fi 重连、语音、音乐与表情。test 通道通过一台设备验证后，
再推广同一版本文件到 stable。构建成功不等于实机验证通过。
