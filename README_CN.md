<p align="center">
  <img src="images/logo.png" alt="PourInput 标志" width="420">
</p>

# PourInput

**One Button. Two Actions.**

[English](README.md) | **简体中文**

开源鼠标自定义工具，专注于 Multi-Action（多操作）输入、Generic Mouse Mode（通用鼠标模式）与更灵活的工作流。

<p>
  <a href="https://github.com/pour-soi/PourInput/releases/download/v1.2.1/PourInput-v1.2.1-Windows.zip">
    <img src="https://img.shields.io/badge/%E4%B8%8B%E8%BD%BD_Windows_%E7%89%88-v1.2.1-0078D4?style=for-the-badge&logo=windows11&logoColor=white" alt="下载 Windows 版">
  </a>
  <a href="https://github.com/pour-soi/PourInput/releases/tag/v1.2.1">
    <img src="https://img.shields.io/badge/%E7%89%88%E6%9C%AC%E8%AF%B4%E6%98%8E-v1.2.1-555555?style=for-the-badge" alt="版本说明">
  </a>
</p>

最新版本：`v1.2.1` · Windows

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![最新版本](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![许可证](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

## 为什么选择 PourInput？

很多鼠标都有额外按键，但一个按键固定绑定一个动作并不总是够用。PourInput 让受支持的鼠标按键可以根据使用方式执行不同操作。

Multi-Action 目前支持分别设置单击操作和长按操作。例如，同一个侧键可以在单击时复制文本，在长按时执行浏览器前进。

通用鼠标模式可以让 Windows 标准中键和侧键事件使用 PourInput 动作，不需要 Logitech HID++，也不需要连接受支持的 Logitech 鼠标。

PourInput 不打算替代 Logitech Options+ 的所有功能。它是一个专注于可配置按键重映射和高级按键操作的开源工具。

## 功能

- **多操作单击 / 长按支持**：受支持按键可以在单击时执行一个动作，在长按时执行另一个动作。
- **通用鼠标模式**：中键、侧键 1 和侧键 2 可以通过 Windows 标准鼠标事件映射到 PourInput 动作，不依赖 Logitech HID++。
- **运行时通用鼠标模式开关**：该模式默认关闭，可在设置中启用；关闭后，受支持按键会恢复原生行为。
- **Logitech 控件保持可用**：受支持的 Logitech 控件仍然可用，并且通用鼠标模式不会创建重复的中键或侧键条目。
- **English / 简体中文界面切换**：用户可以在设置中切换可见应用语言。
- **保存语言偏好**：没有偏好时默认使用 English；选择的语言会保存，并在下次启动时恢复。
- **映射和配置文件兼容**：语言切换只改变可见标签，不会重写动作 ID、按键键名、映射或配置文件数据。
- **基于设备能力的支持基础**：PourInput 根据设备实际暴露的能力启用功能，而不是只依赖静态品牌列表。
- **受支持设备上的 Logitech HID++ 高级功能**：受支持的 Logitech 设备可能提供 Mode Shift、SmartShift、可调 DPI、电量读取、手势控件和水平滚动等能力。
- **按应用切换配置文件**：可以为不同应用自动切换鼠标按键映射。
- **内置截图动作**：可以将全屏或选区截图保存到剪贴板或文件。
- **Windows 便携发布包**：打包版本不需要单独安装 Python。

## 工作方式

打开鼠标页面并选择一个受支持的按键。每个受支持的多操作按键可以显示：

- **单击操作**
- **长按操作**

示例：

- 中键：单击 -> 复制，长按 -> 粘贴
- 侧键 1：单击 -> 复制，长按 -> 浏览器前进
- 侧键 2：单击 -> 粘贴，长按 -> 浏览器后退
- 受支持 Logitech 设备上的 Mode Shift：单击 -> 区域截图到剪贴板，长按 -> 切换滚轮模式

按下时间短于 300 ms 时执行单击操作。按住至少 300 ms 后松开时执行长按操作。

如果没有设置长按操作，该按键会保持加入多操作框架之前的行为。

## 通用鼠标模式

通用鼠标模式支持以下 Windows 标准鼠标按键：

| 按键 | 支持的操作槽位 |
|------|----------------|
| 中键 | 单击操作、长按操作 |
| 侧键 1 | 单击操作、长按操作 |
| 侧键 2 | 单击操作、长按操作 |

通用鼠标模式仅支持 Windows。它默认关闭，需要在设置中手动启用。

该模式不需要连接受支持的 Logitech 鼠标。它会监听 Windows 标准中键和侧键事件，然后执行已配置的 PourInput 单击操作或长按操作。

现有 Logitech 专用控件仍然可用。当连接受支持的 Logitech 鼠标并启用通用鼠标模式时，PourInput 会避免显示重复的中键或侧键条目。

多只标准鼠标目前还不能分别设置不同的通用映射，因为标准 Windows 鼠标事件不会区分事件来自哪一只物理鼠标。

通用鼠标模式不支持左键重映射、右键重映射、向上 / 向下滚动重映射、任意额外鼠标按键，或不会显示为 Windows 标准鼠标事件的厂商专有按键。

## 下载与安装

当前版本：`v1.2.1`

Windows 用户应下载：

```text
PourInput-v1.2.1-Windows.zip
```

直接下载：
[PourInput-v1.2.1-Windows.zip](https://github.com/pour-soi/PourInput/releases/download/v1.2.1/PourInput-v1.2.1-Windows.zip)

版本说明：
[v1.2.1 — Generic Mouse Status Fix](https://github.com/pour-soi/PourInput/releases/tag/v1.2.1)

安装：

1. 下载 `PourInput-v1.2.1-Windows.zip`。
2. 解压 zip 文件。
3. 运行 `PourInput-v1.2.1/PourInput.exe`。
4. 如果已经运行了其他 PourInput 或 PourInput 构建，请先退出后再启动。

Windows 发布包已经包含所需运行文件。使用正式发布包时，不需要另外安装 Python。

首次启动时，PourInput 会自动创建配置文件。没有保存语言偏好时，默认使用 English。

## 平台支持

Windows 是 v1.2.1 唯一的官方公开发布目标。

公开的 GitHub Release 应只包含：

- `PourInput-v1.2.1-Windows.zip`
- `pourinput-v1.2.1-update.json`

macOS 支持已规划，但尚未正式提供。Linux 构建仍属于验证用途，不是官方公开发布目标。

## 设备支持

PourInput 采用基于设备能力的支持架构。它会根据设备实际具备的能力启用相应功能，而不是简单地按照品牌判断“支持”或“不支持”。

带有 Windows 标准中键和侧键的鼠标可以使用通用鼠标模式。受支持的 Logitech 设备还可能暴露额外的 HID++ 功能。

某些 Logitech 控件必须同时支持重新编程和转发拦截，PourInput 才能接管并重映射。如果能力信息缺失或不完整，PourInput 会保守地回退到现有设备目录和通用按键行为，而不会假定设备完整支持所有功能。

### 已测试设备

| 设备 | 状态 |
|------|------|
| 带 Windows 标准中键和侧键的 ZOWIE 鼠标 | 已在 Windows 上通过通用鼠标模式手动验证 |
| MX Master 3 | 已测试已编目的多操作控件和 HID++ 能力检测 |

### 实验性 / 可能兼容设备

以下设备不视为官方已支持，除非已经在 PourInput 中完成实际测试。它们在暴露匹配的 Windows 标准中键 / 侧键事件或 HID++ 能力时可能可用。

| 设备 | 说明 |
|------|------|
| 带中键和侧键的 Windows 标准鼠标 | 可能可通过通用鼠标模式使用中键和侧键的单击 / 长按动作 |
| MX Master 3S | 预计与 MX Master 系列共享多项能力；仍需要用户和设备测试 |
| M720 Triathlon | 暴露所需 HID++ 控件时可能兼容 |
| MX Anywhere 系列 | 暴露所需 HID++ 控件时可能兼容 |
| MX Master 4 / 2S / 初代 MX Master | 暴露所需 HID++ 控件时可能兼容 |
| 其他 Logitech HID++ 设备 | 暴露匹配的可重新编程、可转发拦截控件时可能兼容 |

多操作支持适用于通用鼠标模式中的中键 / 侧键，也适用于已暴露对应控件的受支持 Logitech 设备。DPI、SmartShift、电量、手势控件和水平滚动等设备能力会因设备和固件而异。

如果鼠标已被检测到但缺少某个按键，请在设备支持请求中附上鼠标页面导出的 device info JSON。

## 使用限制

- 通用鼠标模式目前只支持中键、侧键 1 和侧键 2。
- 通用鼠标模式目前还不能按物理设备区分多只标准鼠标。
- 部分 Logitech 功能取决于设备固件和暴露出的 HID++ 能力。
- 双击操作已规划，但尚未实现。
- 长按判定时间固定为 300 ms，暂时不能在界面中配置。
- 宏和连续动作尚未实现。

## 问题排查

- 如果 PourInput 无法启动，请确认已经先解压压缩包，再运行 `PourInput.exe`。
- 如果标准鼠标按键没有显示，请确认已经在设置中启用通用鼠标模式。
- 如果原生中键点击或浏览器返回 / 前进没有恢复，请关闭通用鼠标模式并重新启动 PourInput。
- 如果 Logitech 按键没有显示，设备可能没有暴露所需 HID++ 能力。请在设备支持请求中附上鼠标页面导出的 device info JSON。
- 如果应用语言没有按选择显示，请打开设置重新选择语言，然后重启 PourInput。

## 后续计划

### 已完成

- **多操作单击 / 长按支持**：一个受支持的物理按键可以为单击和长按执行不同动作。
- **通用鼠标模式**：Windows 标准中键、侧键 1 和侧键 2 可以在不依赖 Logitech HID++ 的情况下使用 PourInput 动作；关闭后恢复原生中键点击和浏览器返回 / 前进行为。
- **应用语言切换**：可见界面可以在 English 和简体中文之间切换，并且不会改变已有映射。
- **基于设备能力的支持基础**：PourInput 可以根据检测到的设备能力启用或限制功能，而不是只依赖静态设备列表。

### 计划 / 未来方向

未来开发重点是增强型 Easy-Switch、操作层（Action Layers）和更高级的多操作工作流。

- **增强型 Easy-Switch**：Easy-Switch 是 Logitech 的设备切换功能，可以让受支持鼠标在已配对的电脑或设备之间切换。增强型 Easy-Switch 是 PourInput 计划探索的方向，目标是让用户更方便地在已连接电脑之间切换，而不必只依赖鼠标原本的切换方式。它也可能成为未来跨设备工作流的基础。
- **操作层**：操作层计划让同一个物理鼠标按键在不同层中执行不同功能。这样即使鼠标按键数量有限，也可以通过切换层获得更多可用操作。
- **高级多操作**：这是现有单击与长按系统的未来扩展方向，目标是探索更丰富的按键交互和操作工作流。

这些内容是开发方向，不是已经承诺的功能、固定发布时间或保证交付范围。

## 开发

设计与可视化发布文档请从 [Pour 产品家族设计系统](docs/POUR_DESIGN_SYSTEM.md) 开始阅读。

要求：

- Python 3.12
- `requirements.txt` 中的依赖
- 用于打包构建的 PyInstaller

创建环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

从源代码运行应用：

```powershell
.\.venv\Scripts\python.exe main_qml.py
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

构建 Windows 应用：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller PourInput.spec --noconfirm
```

创建带版本号的 Windows 发布包：

```powershell
.\scripts\create_release.ps1 -Version v1.2.1
```

发布脚本会把带版本号的输出写入 `release/`，并保留 `.git`、源代码、发布历史、设置、日志和已有版本发布包。

## 参与贡献

欢迎贡献文档改进、测试、设备支持数据和聚焦的错误修复。

提交拉取请求前：

1. 保持行为变更小而清晰，并添加相应测试。
2. 运行 `python -m unittest discover -s tests`。
3. 修改鼠标支持时，请包含设备信息 JSON。
4. 修改用户可见行为时，请同步更新文档。

未来如果要添加新的多操作按键：

1. 将按键键名加入多操作按键配置。
2. 确认该按键同时具有按下和松开事件。
3. 添加默认长按映射。
4. 通过后端设备能力数据暴露该按键。
5. 添加聚焦的引擎、配置、后端和界面测试。

更多信息见 [CONTRIBUTING.md](CONTRIBUTING.md)、[CONTRIBUTING_DEVICES.md](CONTRIBUTING_DEVICES.md) 和 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 致谢

PourInput 基于原始 [Mouser](https://github.com/TomBadash/Mouser) 项目。感谢 Mouser 贡献者创建了让本项目成为可能的基础。

PourInput 将继续独立开发，同时保留并尊重对原始工作的署名。

维护者：`pour-soi`

## 许可证

本项目保留原始 Mouser 许可证。详见 [LICENSE](LICENSE)。
