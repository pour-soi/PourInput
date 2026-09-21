<p align="center">
  <img src="images/logo.png" alt="PourInput" width="180">
</p>

# PourInput

### 你的鼠标，由你掌控。

[English](README.md) · **简体中文**

PourInput 是一款鼠标自定义软件。为受支持的按键分配操作，让单击和长按各司其职，再为不同应用配置不同映射。把鼠标调成适合自己的样子，设置保存在本地。

[**下载 Windows 正式版 · v1.4.2**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

[本版更新](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2) · [macOS 版本](#macos-版本) · [反馈问题](https://github.com/pour-soi/PourInput/issues)

![PourInput 鼠标按键与应用配置界面](images/Screenshot_mouse_zh-CN.png)

**按键映射 · 单击与长按 · 应用配置 · MX Master 高级控制**

## 把常用操作放到手边

复制、粘贴、浏览器前进后退、切换标签、截图等内置操作，都可以分配给受支持的鼠标按键。在鼠标页面选择对应按钮，把最常用的命令安排到顺手的位置。

### 一个按键，两种操作

为同一个受支持的按键分别设置**单击**和**长按**操作。例如，短按复制，长按粘贴。按自己的习惯组合，不必让每个按钮只做一件事。

### 换个应用，换套配置

为浏览器、编辑器和其他软件分别创建应用配置，让同一个按键在不同软件中执行不同操作。切换应用时，PourInput 自动选用对应配置；其他场景则使用默认配置。

### 普通鼠标也能自定义

**通用鼠标模式**接管 Windows 标准中键和侧键，适用于 ZOWIE 等提供这些标准输入的鼠标，不需要先连接受支持的罗技设备。

![通用鼠标模式按键配置](images/Screenshot_generic_zh-CN.png)

### 保留 MX Master 的高级能力

设备支持时，可以使用手势、滚轮模式切换、智能切换、DPI 调节、电量显示和水平滚动等 HID++ 功能。实际可用项取决于型号和固件。

通用鼠标模式可以与 MX 高级功能同时使用：开启后，通用模式接管它支持的标准输入，不冲突的 MX 专用功能继续可用。通用映射设为“无操作”就不会执行，也不会回退到 MX 动作。关闭通用模式后恢复设备专用处理，原有映射始终保留。

## 按自己的习惯设置

1. 打开鼠标页面，点击要配置的受支持按键。
2. 选择单击操作，需要时再设置长按操作。
3. 为需要不同操作的软件添加应用配置。
4. 要配置标准中键和侧键时，按需开启通用鼠标模式。

界面可切换简体中文或英文，不影响已保存的映射。设置保存在自己的电脑上。

## 附加功能：Windows 阅读模式

阅读模式是鼠标自定义之外的一项可选功能。将本地 TXT 或 EPUB 放进阅读浮窗，用滚轮手动导航，或开启可调速、可暂停的自动连续滚动。浮窗大小、文字样式和透明度都可以调整。

关闭阅读模式时，滚轮正常滚动页面；开启后，竖向滚轮暂时控制阅读内容，不改变已保存的鼠标映射。按住隐藏键时自动滚动暂停，松开后继续；关闭阅读模式后，鼠标隐藏键恢复原来的操作。

<details>
<summary>展开查看阅读截图与使用说明</summary>

![使用示例文字的阅读浮窗](images/Screenshot_reading_panel_zh-CN.png)

点击左侧书本图标，导入文件并开启阅读模式。在阅读页面点击**开始／继续自动阅读**或**暂停自动阅读**。读到文末会停止，重开软件后恢复保存的位置，并保持暂停。

浮窗有标准、简洁和隐约三种显示方式，保持置顶且不抢焦点；简洁与隐约模式的正文可以鼠标穿透。暂时隐藏时，阅读模式仍接管滚轮。鼠标隐藏键在阅读时只负责隐藏，键盘隐藏键仍保留键盘原有作用。

书籍与阅读位置独立于鼠标配置保存。截图来自实际界面，使用示例文字。更多说明见[阅读模式指南](docs/READING_MODE.md)。

</details>

## 在 Windows 上开始使用

[**下载 PourInput v1.4.2 Windows 正式版**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

1. 将 ZIP **完整解压**到较短的路径，例如 `F:\Apps`。不要直接在压缩包内运行，也不要在解压报错时跳过文件。
2. 从**系统托盘菜单**退出旧版 PourInput。只关闭设置窗口，并不代表软件已经退出。
3. 打开 `PourInput/PourInput.exe`，无需另外安装 Python。
4. 要设置按键，进入鼠标页面，点击对应按钮。
5. 按需添加应用配置；要自定义标准中键和侧键时，开启通用鼠标模式。

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
