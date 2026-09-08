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
- 阿里云 HTTPS 健康接口返回 200；新板型 test 查询返回 404 release not found。
- 自动审批阻止了上传与 test 发布，因此新板型尚未发布到服务器。
- 尚未 USB 刷入、验证实际 OTA 槽切换、资源更新、重连、语音、音乐或表情。
- 云端角色设定稿位于 `prompts/laoyuanxiaozhi-persona.md`，由用户填写到小智后台。

本机日志位于 `logs/build_laoyuanxiaozhi_package_20260908.log` 和
`logs/ota_host_linux_20260908.log`，日志未提交到 Git。
