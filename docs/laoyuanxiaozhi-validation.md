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
- 尚未 USB 刷入、验证实际 OTA 槽切换、资源更新、重连、语音、音乐或表情。
- 云端角色设定稿位于 `prompts/laoyuanxiaozhi-persona.md`，由用户填写到小智后台。

本机日志位于 `logs/build_laoyuanxiaozhi_package_20260908.log` 和
`logs/ota_host_linux_20260908.log`，日志未提交到 Git。
