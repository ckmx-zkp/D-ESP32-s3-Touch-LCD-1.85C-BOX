新增 微雪 开发板: ESP32-S3-Touch-LCD-1.85C
产品链接：
https://www.waveshare.net/shop/ESP32-S3-Touch-LCD-1.85C.htm

## 本目录的 BOX V2 配置

硬件版本已由用户确认为 V2。BOX 是带音箱外壳的版本，使用上游
`waveshare/esp32-s3-touch-lcd-1.85c` 板级实现。
本地 `config.json` 显式选择 `CONFIG_VERSION_2_0=y`，基础板型保持
`esp32-s3-touch-lcd-1.85c`。标准变体保持原名称，云音乐变体使用独立名称
`esp32-s3-touch-lcd-1.85c-box-v2-music`。

## 云音乐变体

参考 `D:\wumingxiaozhi` 移植 `self.music.play_url` 和 `self.music.stop`。
云端 `search_netease_music` 返回临时音频链接后，设备等待当前语音播放结束，
再播放歌曲并显示歌名、歌手；停止命令同时取消待播请求。

本地当前使用音乐变体。后续重新构建请在 ESP-IDF 6.0.2 终端执行：

```powershell
python scripts/build.py waveshare/esp32-s3-touch-lcd-1.85c --name esp32-s3-touch-lcd-1.85c-box-v2-music --language zh-CN
```

普通变体不启用云音乐工具。云端 MCP 接入信息和验证方法见
`deploy/music-mcp/README.md`。MCP 令牌不在固件中。
可对设备说“用网易云播放胡大强的庸人自娱”，再说“停止音乐”验证。

### 硬件参数

以下引脚来自本目录的 `config.h` 和板级初始化代码。

| 功能 | 配置 |
| --- | --- |
| 芯片 | ESP32-S3，240 MHz |
| Flash / PSRAM | 16 MB QIO / 8 MB Octal，PSRAM 80 MHz |
| 分区 | `partitions/v2/16m.csv`，双 OTA 应用分区和 8 MB assets |
| 屏幕 | ST77916，360 x 360，QSPI，RGB565 |
| LCD 时钟 / CS | GPIO40 / GPIO21 |
| LCD D0 / D1 / D2 / D3 | GPIO46 / GPIO45 / GPIO42 / GPIO41 |
| 背光 | GPIO5，PWM，高电平有效 |
| 共用 I2C | SDA GPIO11，SCL GPIO10 |
| LCD / 触摸复位 | TCA9554 EXIO0 / EXIO1，由上游代码同时复位 |
| V2 音频 | ES8311 播放 + ES7210 采集，输入/输出 24 kHz |
| I2S MCLK / BCLK / WS | GPIO2 / GPIO48 / GPIO38 |
| I2S DOUT / DIN | GPIO47 / GPIO39 |
| 功放使能 | GPIO15 |
| BOOT 按钮 | GPIO0，点击切换对话，启动阶段点击进入配网 |
| 触摸中断定义 | GPIO4；当前板级代码未初始化触摸驱动 |

不能将 V1 的独立 I2S 麦克风配置用于 V2。当前上游虽然复位触摸芯片并定义了
触摸引脚，但没有注册触摸输入，不能把显示可用等同于触摸可用。
本次也未添加电池电量、SD 卡等外围功能。音频参考输入沿用上游设置，
不代表已启用或验证设备端 AEC。

### 本机环境

- ESP-IDF：`D:\esp-idf\v6.0.2\esp-idf`，版本 6.0.2。
- 工具目录：`D:\esp-tool`。
- Python：`D:\esp-tool\python_env\idf6.0_py3.13_env\Scripts\python.exe`。
- 根目录 `idf-local.cmd` 在独立环境中执行 ESP-IDF 命令，可直接从 PowerShell 调用。
- 本地 `.vscode/settings.json` 已指定以上环境和 `esp32s3` 目标，该文件被上游 Git 忽略。

从项目根目录使用已经生成的本地配置：

```powershell
.\idf-local.cmd --version
.\idf-local.cmd menuconfig
.\idf-local.cmd build
```

本地语言选择为简体中文。查看硬件版本的菜单路径：
`Xiaozhi Assistant -> Board Type -> Waveshare ESP32-S3-Touch-LCD-1.85C`，
然后在 `ESP32S3_TOUCH_LCD_1_85C version` 中选择 `version 2.0`。

如果删除了 build 或 sdkconfig，或者需要按上游方式生成合并固件，
先在 ESP-IDF 6.0.2 终端进入项目根目录，再执行：

```powershell
python scripts/build.py waveshare/esp32-s3-touch-lcd-1.85c --name esp32-s3-touch-lcd-1.85c --language zh-CN
```

该命令会重新生成板级配置、编译并生成 `build/merged-binary.bin`。
用户后续指定编译并烧写至 `COM11`，本地 VS Code 也已选择该串口。
构建及烧录日志保存在项目根目录 `logs/`，串口监视脚本为
`scripts/monitor-com.ps1`，使用 115200 8N1、UTF-8 日志和 PID 文件。
实物显示、录音、播放、唤醒和联网对话仍需在烧录后分别验证。

### 2026-09-07 验证记录

- ESP-IDF 6.0.2 配置生成和完整编译成功，应用大小 `0x2ad510` 字节，
  `0x3f0000` 字节 OTA 应用分区剩余 32%。
- `COM11` 识别为 ESP32-S3 revision v0.2，内置 8 MB PSRAM。
- bootloader、分区表、OTA 数据、资源和应用五个镜像均通过烧录哈希校验。
- 复位后的日志确认 8 MB PSRAM、QIO Flash、ST77916/LVGL、
  ES8311/ES7210 和音频设备初始化成功。
- 设备进入 `wifi_configuring`，热点 `Xiaozhi-EC5D`，
  配网页面 `http://192.168.4.1`；尚未验证联网对话及实物声画效果。
- 上游屏幕初始化有一次 GPIO21 重复配置警告，发生在低速读屏幕 ID 后重新创建
  高速 SPI IO；随后屏幕初始化继续成功。此记录不等同于警告已修复。
- 构建日志：`logs/build_COM11_20260907_103606.log`。
- 烧录日志：`logs/flash_COM11_20260907_104438.log`。
- 启动日志：`logs/COM11_20260907_104550.log`。
- 监视进程信息：`logs/COM11_monitor.json`，PID 文件：`logs/COM11_monitor.pid`。
  再次烧录前应先停止该 PID 对应的监视进程，释放串口。

### 人物全屏表情版

构建名称：`esp32-s3-touch-lcd-1.85c-box-v2-music-portrait`。
保留 BOX V2 音频引脚及私人云音乐功能，新增 `CONFIG_BOX_V2_PORTRAIT_EMOJI`。
本机可执行 `scripts\build-box-v2-portrait.cmd`，或在 ESP-IDF 环境中执行：

```powershell
python scripts/build.py waveshare/esp32-s3-touch-lcd-1.85c --name esp32-s3-touch-lcd-1.85c-box-v2-music-portrait --language zh-CN
```

- `assets/emoji/` 包含全部 21 个标准情绪名称的 360×360 PNG，替换默认 Noto 表情。
- 人物脸型较初稿略长；全屏白底，人物绘图区最高 316 像素，保留圆屏边缘及状态文字空间。
- `portrait_display.h` 将状态文字放在顶部窄区，网络/静音图标和滚动字幕放在下方衣服区域。
- 开机、联网、下载和错误状态映射到人物表情；未知情绪回退到 `neutral`。
- 表情为静态 PNG，依云端下发的情绪名称切换，不含逐帧口型动画。
- `scripts/prepare_portrait_assets.py` 可从已保存的生成原图重新裁切并校验表情名称、尺寸和 SHA-256。
  其中第二张原图使用人工核对后的行边界，避免裁入相邻表情。
- 生成模式为 `edit`：两张方图实际 1254×1254，一张横图实际 2172×724；
  未达到生成请求的 2048×2048 / 3072×1024。固件资源均由原图缩小制作，没有放大冒充原生分辨率。
- 生成提示词、原图及 `.meta.json` 分别位于根目录 `prompts/` 和 `generated/`；
  资源清单位于 `assets/portrait-manifest.json`，圆屏裁切预览为
  `generated/portrait-firmware-round-preview.png`，该预览不是设备截图。

重新烧录需要同时写入应用和 `assets` 分区：释放串口监视进程后执行
`idf-local.cmd -p COM11 flash`，随后重新启动 `scripts/monitor-com.ps1`。
不使用整片擦除，保留已有 Wi-Fi 和激活信息。旧版构建名称继续保留。

2026-09-07 人物版验证结果：

- 69 项主机测试通过；`git diff --check` 和新增显示类格式检查通过。
- 最终应用 `2,813,840` 字节，OTA 槽剩余 32%；资源包 `4,003,871` 字节。
- 从待烧录资源包逐项提取校验，全部 21 张图片的 SHA-256 与源资源一致，
  字体和唤醒模型仍在包内。校验脚本为 `scripts/verify_portrait_assets.py`。
- COM11 首次打开遇到拒绝访问，串口释放后重试成功，五个镜像均通过哈希校验。
  随后按字体实际 23 像素行高修正文字栏及图标间距，再次编译并以 `app-flash`
  更新应用，通过哈希校验，资源包保持不变。
- 启动日志确认新构建名称、`Full-screen portrait layout: 360x360`、
  `robot_2 -> neutral`、Wi-Fi/MQTT 连接及 `activating -> idle`，
  `self.music.play_url` / `self.music.stop` 注册成功。
- 最终启动后的对话日志覆盖全部 21 个情绪名称的映射调用，未出现图片解码错误或崩溃。
  部分调用连续到达，不能由此推断每张图片都在屏幕上停留了足够时间；
  未通过实物照片核验屏幕观感，也未重新验证音乐可闻播放。
- 最终日志：`logs/build_portrait_final_COM11_20260907.log`、
  `logs/flash_portrait_final_COM11_20260907.log`、
  `logs/COM11_portrait_final_20260907_125633.log`。
  完整资源烧录记录为 `logs/flash_portrait_COM11_20260907_retry.log`。
- 串口监视 PID 为 `31972`，实时信息仍以 `logs/COM11_monitor.json` 为准。

### 来源

- 官方源码：https://github.com/78/xiaozhi-esp32
- 厂商 BOX/裸板共用说明：https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.85C
- 本次拉取基线：`c7241272f2d5fd140c77542f3cf12d09e717fc2f`（2026-09-07 拉取）。
