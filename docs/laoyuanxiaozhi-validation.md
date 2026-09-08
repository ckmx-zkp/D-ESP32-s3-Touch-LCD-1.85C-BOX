# laoyuanxiaozhi 验证记录（2026-09-08）

- 新增独立板型 `laoyuanxiaozhi`，复用 BOX V2 原引脚与硬件实现。
- ESP-IDF 6.0.2 规范构建及打包成功，命令退出码为 0。
- 应用 2.4.2：2,817,136 字节，OTA 应用槽剩余 32%。
- assets：4,003,871 字节，位于 8 MB 资源分区。
- 迁移包：`releases/v2.4.2_laoyuanxiaozhi.zip`。
- 编译数据库仅包含一个非 common 板级翻译单元，即新板型包装源文件。
- Linux 主机测试 69 项全部通过；OTA 服务端测试 6 项全部通过。
- Windows 主机测试最初遇到 5 项临时目录占用错误；转 Linux 后通过。
- C/C++ clang-format 检查、git diff --check、发布脚本和验证脚本语法检查通过。
- 用户明确授权后，2.4.2 固件和资源已发布到阿里云 `laoyuanxiaozhi/test` 通道。
- 私有接口返回正确板型和版本；Ubuntu Python 使用指定 CA 完成 HTTPS 下载校验。
- 固件与资源的下载长度、清单 SHA-256 和本地构建 SHA-256 全部一致。
- 固件 SHA-256：`4979046100b72c772770329bdbddf2d6956da9dec2b27a0ddc5cef5af0ed8794`。
- 资源 SHA-256：`44c46a0597120f83faa950b948cb14efb0429355ead110c96d2daf94e157fd9f`。
- 本次仅发布 test 通道，未推广到 stable。
- COM11 已通过 USB 迁移到 2.4.2，写入校验通过；原分区表一致，NVS 区域未写入。
- 设备以 `laoyuanxiaozhi` 身份启动，保留原 UUID 和 Wi-Fi 配置。
- 设备从阿里云下载 2.4.2 assets，完成资源更新并恢复 MQTT/idle。
- 实际发声与屏幕视觉效果仍需现场验收。
- 云端角色设定稿位于 `prompts/laoyuanxiaozhi-persona.md`，由用户填写到小智后台。

本机日志位于 `logs/build_laoyuanxiaozhi_package_20260908.log` 和
`logs/ota_host_linux_20260908.log`，日志未提交到 Git。

迁移烧写日志：`logs/flash_laoyuanxiaozhi_COM11_20260908_200849.log`。
迁移监控日志：`logs/COM11_laoyuanxiaozhi_20260908_201028.log`。

## 2.4.3 升级表情修复

- 固件与资源升级直接显示内置 thinking.png，不依赖资源集合的加载状态。
- 原始 132,771 字节 PNG 已逐字节确认包含于新应用镜像。
- ESP-IDF 6.0.2 构建与 ZIP 打包成功，退出码 0；69 项主机测试通过。
- 迁移包为 `releases/v2.4.3_laoyuanxiaozhi.zip`。
- 用户明确授权本项目所有版本发布和烧写后，2.4.3 已发布至 test 通道。
- HTTPS 下载的固件及资源大小、SHA-256 均与本地构建和服务端清单一致。
- COM11 实机从 2.4.2 OTA 升级至 2.4.3，进入 ota_1 并标记固件有效。
- 资源升级日志确认调用 `Built-in thinking background: cloud_download`。
- 资源版本更新至 2.4.3，随后 MQTT 连接成功，恢复 idle；串口监控持续运行。
- 本次资源内容与 2.4.2 相同，发布脚本同步递增资源版本导致额外下载；并非固件升级失败重试。
- 恢复阶段出现 SSL receive failed -76 和 I2S disable 未启用提示，未阻止后续版本检查和 MQTT/idle；不宣称日志零错误。
- 画面的实际视觉效果与发声仍需现场确认。
- 构建日志为 `logs/build_laoyuanxiaozhi_243_20260908.log`。

构建文件校验：

```json
{
  "xiaozhi.bin": {
    "size": 2950112,
    "sha256": "4e5e8a265a1a33959f77e10564dee8c84d748d8242c2928d143d42d702e786ae"
  },
  "generated_assets.bin": {
    "size": 4003871,
    "sha256": "44c46a0597120f83faa950b948cb14efb0429355ead110c96d2daf94e157fd9f"
  }
}
```

2.4.3 实机 OTA 日志：`logs/COM11_ota243_20260908_202716.log`。
