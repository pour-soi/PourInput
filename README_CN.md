<p align="center">
  <img src="images/logo.png" alt="PourInput logo" width="96">
</p>

# PourInput

**一个按键，两个动作。**

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![License](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

PourInput 是基于 [TomBadash/Mouser](https://github.com/TomBadash/Mouser) 的开源项目，面向 Logitech HID++ 鼠标，提供通用的 Multi-Action Button 框架。

当前版本：`v1.0.0`

仓库：`pour-soi/PourInput`

## 功能

- 通用 **Multi-Action** 框架 — 支持的按键可以在 **Click** 和 **Long Press** 时执行不同动作。
- **扩展按键自定义** — 为支持的按键分配独立的 Click 和 Long Press 动作，包括 **Mode Shift**、**Back** 和 **Forward**。
- 改进 **Mode Shift** 处理 — 提供更可靠的事件检测和 HID++ 同步。
- 按应用配置文件 — 自动为不同应用切换按键映射。
- 基于能力的设备支持 — 在可以检测到 HID++ 能力时，按实际能力启用 DPI、SmartShift、电量、手势和额外按键等功能。
- 指针、滚动和 SmartShift 控制 — 配置受支持的 Logitech 设备功能。
- 内置截图动作 — 将全屏或选定区域捕获到剪贴板或文件。
- Windows 便携发布包 — 无需安装 Python。

## 截图

### 主窗口

配置当前设备、配置文件和支持的鼠标按键映射。

![主窗口](assets/screenshot-main.png)

### Multi-Action 配置

为 Click 或 Long Press 槽位选择动作。

![Multi-Action 配置](assets/screenshot-actions.png)

### 关于

显示版本、维护者、上游项目、构建模式、提交和启动路径。

![关于](assets/screenshot-about.png)

## 安装

1. 打开 [最新 Release 页面](https://github.com/pour-soi/PourInput/releases/latest)。
2. 下载 `PourInput-v1.0.0-Windows.zip`。
3. 解压 zip 文件。
4. 运行 `PourInput-v1.0.0/PourInput.exe`。

如果已经运行其他 PourInput 构建，请先从系统托盘退出。

## 支持设备

PourInput 现在采用基于能力的设备支持模型。应用仍保留已编目的设备布局和已知设备元数据，但运行时行为会尽量依据当前鼠标实际暴露的 HID++ 功能和控件来决定。在可检测的情况下，HID++ 能力会用于启用或限制可重映射按键、手势控制、SmartShift、可调 DPI、电量、水平滚动和设备专有控件等功能。

某些按键必须同时支持 reprogrammable 和 divertable，PourInput 才能拦截并重新映射。如果能力信息缺失或不完整，PourInput 会保守地回退到现有设备目录和通用按键行为，而不是假定设备完整支持所有功能。

### 已测试设备

| 设备 | 状态 |
|------|------|
| MX Master 3 | 已测试已编目的 Multi-Action 控件和 HID++ 能力检测 |

### 实验性 / 潜在兼容设备

以下设备不视为官方已支持，除非已经在 PourInput 中完成实际测试。它们在暴露匹配 HID++ 能力时可能可用。

| 设备 | 说明 |
|------|------|
| MX Master 3S | 预计与 MX Master 系列共享多项能力；仍需要用户和设备测试 |
| M720 Triathlon | 暴露所需 HID++ 控件时可能兼容 |
| MX Anywhere 系列 | 暴露所需 HID++ 控件时可能兼容 |
| MX Master 4 / 2S / 初代 MX Master | 暴露所需 HID++ 控件时可能兼容 |
| 其他 Logitech HID++ 设备 | 暴露匹配的 reprogrammable、divertable 控件时可能兼容 |

Multi-Action 当前重点支持 Mode Shift、Back 和 Forward。DPI、SmartShift、电量、手势控制和水平滚动等能力会因设备和固件而异。

如果设备被检测到但缺少某个按键支持，请在 GitHub issue 中附上 Mouse 页面复制出的 device info JSON。

## 从源码运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
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

## 打包发布

```powershell
.\scripts\create_release.ps1 -Version v1.0.0
```

输出文件：

```text
release/
    PourInput-v1.0.0-Windows.zip
    RELEASE_NOTES-v1.0.0.md
    CHANGELOG.md
```

## 已知限制

- v1.0.0 的官方发布目标仅限 Windows。
- PourInput 面向 Logitech HID++ 设备。
- 部分功能取决于设备固件和暴露出的 HID++ 能力。
- macOS 支持已规划，但尚未正式提供。
- Double Click 已规划，但尚未实现。
- Long Press 超时固定为 300 ms，暂不能在界面中配置。
- Macro 和连续动作尚未实现。

## 路线图

### 当前 (v1.0.0)

- Multi-Action 框架
- Click / Long Press 动作
- Mode Shift 改进
- 独立 PourInput 品牌

### 计划

- 增强 Easy-Switch
- 更多可自定义按键动作
- 更好的设备检测
- 配置导入 / 导出
- macOS 实验性支持
- 类似 Flow 的多设备功能（长期）

## 贡献

欢迎提交文档改进、测试、设备信息、bug 修复和新设备支持。添加新设备前请阅读 [CONTRIBUTING_DEVICES.md](CONTRIBUTING_DEVICES.md)。开发说明见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 致谢

PourInput 基于原始 [Mouser](https://github.com/TomBadash/Mouser) 项目。感谢 Mouser 贡献者创建了让本项目成为可能的基础。

PourInput 将继续独立开发，同时尊重并致谢原始项目。

维护者：`pour-soi`

## License

本项目保留原始 Mouser 许可证。详见 [LICENSE](LICENSE)。
