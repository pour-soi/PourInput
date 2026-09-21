<p align="center">
  <img src="images/logo.png" alt="PourInput" width="180">
</p>

# PourInput

### 让鼠标更顺手，让阅读跟上你的节奏。

[English](README.md) · **简体中文**

为鼠标按键安排顺手的操作，也给正在读的书留一个位置。PourInput 将按应用切换的鼠标快捷操作和桌面阅读浮窗放在一起，支持导入本地 TXT、EPUB，以及平滑的自动连续阅读。

[**下载 Windows 正式版 · v1.4.2**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

[本版更新](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2) · [macOS 版本](#macos-版本) · [反馈问题](https://github.com/pour-soi/PourInput/issues)

![PourInput 自动连续阅读浮窗](images/Screenshot_reading_panel_zh-CN.png)

**鼠标快捷操作 · 自动连续阅读 · 设置保存在本地**

## 给阅读留一个随时可见的位置

导入本地 TXT 或 EPUB，文字就能显示在其他窗口上方的阅读浮窗中。拖动书页嫩芽图标移动浮窗，拖动右下角调整大小，再选一个看着舒服的字号和文字颜色。

### 想自己滚，就自己滚；想自动读，就自动读

用鼠标滚轮手动导航，也可以开启自动阅读，让文字平滑地向上移动。速度可以调，随时能够暂停，再从原处继续。滚动过程中，浮窗大小和字号保持不变。

读到文末会自动停止。阅读位置会保存；重新打开软件后，回到保存的位置，等待你手动开始自动阅读。

### 需要时看见，不需要时藏起来

提供**标准、简洁、隐约**三种显示方式。浮窗保持置顶，不抢走键盘输入焦点；简洁和隐约模式的正文区域可以鼠标穿透，独立的移动与缩放把手仍可操作。背景也可以完全透明，只留下文字。

按住隐藏键，浮窗就会消失，自动滚动也同时暂停。松开后重新出现，从刚才的位置继续，不会在看不见的时候偷偷往下读。

![简体中文阅读页面：自动阅读、速度和外观设置](images/Screenshot_reading_zh-CN.png)

*阅读截图来自实际软件界面，使用示例文字展示。*

## 让鼠标按键适应你的习惯

为受支持的按键分别设置**单击**和**长按**操作。复制、粘贴、切换浏览器标签、截图等常用动作，都可以安排到手边。还可以为不同应用保存不同配置，让同一个按键在不同软件中执行不同操作。

**普通鼠标也能用。** 通用鼠标模式接管 Windows 标准中键和侧键，适用于 ZOWIE 等能提供这些标准输入的鼠标，不需要先连接受支持的罗技设备。

**MX Master 保留高级功能。** 设备支持时，可以使用手势、滚轮模式切换、智能切换、DPI、电量显示和水平滚动等 HID++ 功能。实际可用项取决于型号和固件。

**一个输入，只由一处处理。** 开启通用鼠标模式后，它独占支持的标准输入；映射设为“无操作”就是不执行，不会偷偷回退到保存的 MX 映射。不冲突的 MX 专用功能仍可使用，切换模式也不会删除原来的设备映射。

## 阅读和鼠标功能如何配合

- **关闭阅读模式：** 滚轮正常滚动当前网页或应用。
- **开启阅读模式：** 竖向滚轮控制阅读内容，不再带动后面的页面；与通用鼠标模式开关无关。
- **用鼠标按钮隐藏：** 阅读时，该按钮只负责隐藏和恢复浮窗。关闭阅读模式后，恢复原来的按键功能。
- **浮窗暂时隐藏时：** 阅读模式仍接管滚轮；隐藏不会退出阅读，也不会重置位置。
- **用键盘按键隐藏：** 键盘按键仍保留原有作用；隐藏键独占处理目前适用于鼠标按钮。

书籍和阅读位置独立保存，不混在鼠标配置文件里。切换鼠标配置不会把正在读的书和进度重置。

## 在 Windows 上开始使用

[**下载 PourInput v1.4.2 Windows 正式版**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

1. 将 ZIP **完整解压**到较短的路径，例如 `F:\Apps`。不要直接在压缩包内运行，也不要在解压报错时跳过文件。
2. 从**系统托盘菜单**退出旧版 PourInput。只关闭设置窗口，并不代表软件已经退出。
3. 打开 `PourInput/PourInput.exe`，无需另外安装 Python。
4. 要设置按键，进入鼠标页面，点击对应按钮。
5. 要阅读，点击左侧**书本图标**，导入 TXT 或 EPUB，开启**阅读模式**。点击**开始／继续自动阅读**，文字就会连续滚动。

Windows 程序尚未签名。[发布页](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2)同时提供 SHA-256 校验文件和更新清单。

## 设备与平台说明

**Windows 实机验证：** 已使用 MX Master 4 和一只 ZOWIE 鼠标验证阅读、滚轮接管及按住隐藏等流程。此前也测试过 MX Master 3 控件。这不代表每个型号、每种固件都能提供全部功能。

通用鼠标模式目前支持中键和两个侧键，暂不能按物理来源区分多只普通鼠标，也不提供通用的左／右键或竖向滚轮重映射。阅读模式对滚轮的接管是独立功能。

其他罗技型号在提供所需 HID++ 控件时可能兼容。如果软件检测到了鼠标，却没有显示某个控件，可以在鼠标页面导出设备信息，并附在[设备支持反馈](https://github.com/pour-soi/PourInput/issues)中。

### macOS 版本

macOS 单独提供 **v1.3.4-macos.1**。上面介绍的 Windows 阅读和自动滚动功能，不包含在这个 macOS 版本中。

[Apple Silicon 下载](https://github.com/pour-soi/PourInput/releases/download/v1.3.4-macos.1/PourInput-1.3.4-macOS-arm64.zip) · [Intel 下载](https://github.com/pour-soi/PourInput/releases/download/v1.3.4-macos.1/PourInput-1.3.4-macOS-x86_64.zip) · [macOS 版本说明](https://github.com/pour-soi/PourInput/releases/tag/v1.3.4-macos.1)

解压对应版本，打开 `PourInput.app`，按提示授予辅助功能权限。此版本尚未签名和公证。Intel 版曾使用 MacBook Air 和 MX Master 3 实测；Apple Silicon 目前仅通过构建验证。通用鼠标模式仅支持 Windows，Linux 仍处于验证阶段。

## 常见问题

**文字一直动，怎么停？** 在阅读页面点击**暂停自动阅读**。按住隐藏键只是临时暂停，松开后会继续。

**按钮执行了预想之外的动作？** 检查当前应用配置、通用鼠标模式，以及这个按钮是否被选作阅读隐藏键。

**解压提示“路径太长”？** 取消解压，换一个更短的目标路径重新完整解压，不要跳过失败的文件。

**打开软件好像没有反应？** 先看看系统托盘中是否已有 PourInput 运行。打开另一个版本前，先退出旧进程。

## 开发与参与贡献

开发请参阅[开发指南](DEVELOPMENT.md)、[架构概览](docs/ARCHITECTURE.md)和[阅读模式说明](docs/READING_MODE.md)。提交改进前，请阅读[贡献指南](CONTRIBUTING.md)与[设备支持指南](CONTRIBUTING_DEVICES.md)。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main_qml.py
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

由 **pour-soi** 维护。早期开发使用了 [Mouser](https://github.com/TomBadash/Mouser) 的部分工作；PourInput 现已独立维护，运行时不需要 Mouser。

[MIT 许可证](LICENSE) · [更新记录](CHANGELOG.md) · [问题反馈](https://github.com/pour-soi/PourInput/issues)
