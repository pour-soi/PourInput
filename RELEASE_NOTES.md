# PourInput v1.4.0 — Reading Mode / 阅读模式

## English

Windows release with local TXT/EPUB reading, a floating panel, fixed-font continuous pagination, direct move/resize controls, transparent background, custom text color/size, and hold-to-hide. Reader state is separate from mouse profiles and the main config. Generic standard-input ownership and non-overlapping MX enhancements are preserved.

Retains all v1.3.5 configuration-loss protection. Unrelated Windows device-change notifications refresh hooks without forcing a healthy HID connection to reconnect. Includes reader hold-button release fixes.

Download the Windows ZIP, extract it, quit any older PourInput process, then run PourInput/PourInput.exe. The existing macOS release remains available separately; this release does not claim Reading Mode hardware validation on macOS/Linux.

Validated on Windows with MX Master 4 and Zowie through user hardware testing; continuous page filling and fixed font behavior were accepted by the tester. Automated checks and packaged-build evidence are recorded in docs/RELEASE_VALIDATION-v1.4.0.md. The Windows executable is unsigned.

## 简体中文

新增本地 TXT / EPUB 阅读模式：置顶浮窗、固定字号连续分页、直接拖动移动和缩放、透明背景、自定义文字颜色与字号，以及按住暂时隐藏。阅读进度独立于鼠标配置，文档内容不会写入主配置文件。保留通用鼠标的输入优先权及不冲突的 MX 高级功能。

完整保留 v1.3.5 的配置丢失防护。无关设备变化只刷新输入钩子，不再强制重连健康的 HID 连接；同时修复阅读隐藏键的部分释放路径。

下载 Windows ZIP 并解压，先退出旧版，再运行 PourInput/PourInput.exe。macOS 现有版本继续单独提供；本次未验证 macOS/Linux 上的阅读硬件行为。

已由用户在 Windows 上使用 MX Master 4 和 Zowie 验证，固定字号和连续填页效果已获确认。自动检查及打包验证见 docs/RELEASE_VALIDATION-v1.4.0.md。Windows 程序暂未进行代码签名。
