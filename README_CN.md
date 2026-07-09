<p align="center">
  <img src="images/logo.png" alt="PourInput logo" width="96">
</p>

# PourInput

**一个按键，两个动作。**

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![License](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

PourInput 是一款开源鼠标自定义工具，专注于高级按键操作与 Multi-Action（多操作）输入。

PourInput 最初基于 [Mouser](https://github.com/TomBadash/Mouser) 开发，如今已逐步形成自己的 Multi-Action 系统、设备能力架构、Generic Mouse Mode（通用鼠标模式）和独立开发路线。

当前版本：`v1.1.0`

仓库：`pour-soi/PourInput`

## 为什么使用 PourInput？

许多鼠标都有额外按键，但一个按键只绑定一个动作并不总是够用。PourInput 的目标是让受支持的鼠标按键变得更灵活，同时保持输入路径清晰、可检查、可调试。

Multi-Action 让一个物理按键可以根据不同的使用方式执行不同操作。目前，PourInput 支持为单击和长按分别设置动作。例如，同一个侧键可以在单击时复制文本，在长按时执行浏览器前进。

Generic Mouse Mode 让使用 Windows 标准中键和侧键的普通鼠标也能使用 PourInput，无需依赖 Logitech HID++。支持的按键可以分别设置单击和长按操作；关闭该模式后，中键点击和侧键返回 / 前进会恢复原生行为。

相比 Logitech Options+，PourInput 是开源项目，更容易审查、脚本化和调试。它并不打算替代 Options+ 的所有功能，而是专注于可配置的按键重映射和高级按键操作。

## 功能

- **Multi-Action 单击 / 长按支持**：受支持的按键可以在单击时执行一个动作，在长按时执行另一个动作。
- **Generic Mouse Mode 支持 Windows 标准中键和侧键**：使用 Windows 标准中键 / 侧键事件的鼠标可以在不依赖 Logitech HID++ 的情况下使用 PourInput；该功能已通过 ZOWIE 鼠标手动验证。
- **Generic Mouse Mode 运行时开关**：关闭该模式时，PourInput 会移除活动的中键 / 侧键回调和拦截，使中键点击和浏览器返回 / 前进恢复原生行为，无需重启应用。
- **基于设备能力的支持架构**：PourInput 会根据设备实际具备的能力开放相应功能，而不是简单按品牌判断“支持”或“不支持”。
- **Logitech HID++ 高级功能**：受支持的 Logitech 设备可能提供 Mode Shift、SmartShift、可调 DPI、电量读取、手势控制和水平滚动等额外能力。
- **按应用切换配置**：可以为不同应用自动切换鼠标按键映射。
- **内置截图动作**：可将全屏或选区截图保存到剪贴板或文件。
- **Windows 便携发布包**：使用正式发布包时无需安装 Python。

## 截图

### 主窗口

在鼠标页面配置当前设备、配置文件和受支持的按键映射。

![主窗口](assets/screenshot-main.png)

### Multi-Action 配置

为受支持的 Click 或 Long Press 槽位选择动作。

![Multi-Action 配置](assets/screenshot-actions.png)

### 关于

查看 PourInput 版本、维护者、上游致谢、构建模式、提交信息和启动路径。

![关于](assets/screenshot-about.png)

## 安装

1. 打开 [最新 Release 页面](https://github.com/pour-soi/PourInput/releases/latest)。
2. 下载 `PourInput-v1.1.0-Windows.zip`。
3. 解压 zip 文件。
4. 运行 `PourInput-v1.1.0/PourInput.exe`。
5. 如果已经运行了其他 PourInput 或 PourInput 构建，请先退出后再启动。

Windows 发布包已经包含所需运行环境，使用正式发布包时不需要单独安装 Python。

## 使用

打开 Mouse 页面并选择一个受支持的按键。

每个受支持的按键可以显示：

- **Click Action**
- **Long Press Action**

示例：

- Middle Button：单击 -> Copy，长按 -> Paste
- Side Button 1：单击 -> Copy，长按 -> Browser Forward
- Side Button 2：单击 -> Paste，长按 -> Browser Back
- 受支持 Logitech 设备上的 Mode Shift：单击 -> 截图选区到剪贴板，长按 -> 切换滚轮模式

按下时间短于 300 ms 时执行 Click Action。按住至少 300 ms 后松开时执行 Long Press Action。

如果没有设置 Long Press Action，该按键会保持加入 Multi-Action 之前的行为。

### Generic Mouse Mode

Generic Mouse Mode 是 Windows 专用模式，面向标准鼠标中键和侧键事件。它不需要 Logitech HID++，因此当非 Logitech 鼠标的中键和侧键报告为 Windows 标准鼠标事件时，也可以使用 PourInput 动作。

当前实现只适用于 Windows 标准中键事件和标准侧键事件。它支持单击和长按动作，支持运行时开启 / 关闭，并且在关闭后恢复原生中键点击和返回 / 前进行为。

这不代表 PourInput 已经支持所有鼠标、所有鼠标按键、所有操作系统，也不支持那些不会显示为 Windows 标准鼠标事件的厂商专有按键。PourInput 目前也还不能可靠地区分多只标准鼠标上的按键来源。

## 支持设备

PourInput 采用 capability-based device support（基于设备能力的支持）思路。也就是说，PourInput 会根据设备实际具备的能力开放相应功能，而不是简单地按照品牌判断“支持”或“不支持”。例如，带有 Windows 标准中键和侧键的鼠标可以使用 Generic Mouse Mode，而受支持的 Logitech 设备还可以使用额外的 HID++ 功能。

某些 Logitech 控件必须同时支持 reprogrammable 和 divertable，PourInput 才能拦截并重新映射。如果能力信息缺失或不完整，PourInput 会保守地回退到现有设备目录和通用按键行为，而不会假定设备完整支持所有功能。

### 已测试设备

| 设备 | 状态 |
|------|------|
| 带 Windows 标准中键和侧键的 ZOWIE 鼠标 | 已在 Windows 上通过 Generic Mouse Mode 手动验证 |
| MX Master 3 | 已测试已编目的 Multi-Action 控件和 HID++ 能力检测 |

### 实验性 / 潜在兼容设备

以下设备不视为官方已支持，除非已经在 PourInput 中完成实际测试。它们在暴露匹配的 Windows 标准中键 / 侧键事件或 HID++ 能力时可能可用。

| 设备 | 说明 |
|------|------|
| 带中键和侧键的 Windows 标准鼠标 | 可能可通过 Generic Mouse Mode 使用中键和侧键单击 / 长按动作 |
| MX Master 3S | 预计与 MX Master 系列共享多项能力；仍需要用户和设备测试 |
| M720 Triathlon | 暴露所需 HID++ 控件时可能兼容 |
| MX Anywhere 系列 | 暴露所需 HID++ 控件时可能兼容 |
| MX Master 4 / 2S / 初代 MX Master | 暴露所需 HID++ 控件时可能兼容 |
| 其他 Logitech HID++ 设备 | 暴露匹配的 reprogrammable、divertable 控件时可能兼容 |

Multi-Action 支持适用于 Generic Mouse Mode 中键 / 侧键，也适用于已暴露对应控件的受支持 Logitech 设备。DPI、SmartShift、电量、手势控制和水平滚动等设备能力会因设备和固件而异。

如果设备被检测到但缺少某个按键，请在 GitHub issue 中附上 Mouse 页面复制出的 device info JSON。

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
.\scripts\create_release.ps1 -Version v1.1.0
```

输出文件：

```text
release/
    PourInput-v1.1.0-Windows.zip
    RELEASE_NOTES-v1.1.0.md
    CHANGELOG.md
```

## 已知限制

- v1.1.0 的官方发布目标仅限 Windows。
- Generic Mouse Mode 目前只支持 Windows 标准中键事件和标准侧键事件。
- Generic Mouse Mode 目前还不能按设备区分多只标准鼠标。
- 不会显示为 Windows 标准鼠标事件的厂商专有按键不属于 Generic Mouse Mode 的支持范围。
- 部分 Logitech 功能取决于设备固件和暴露出的 HID++ 能力。
- macOS 支持已规划，但尚未正式提供。
- Double Click 已规划，但尚未实现。
- Long Press 超时固定为 300 ms，暂时不能在界面中配置。
- Macro 和连续动作尚未实现。

## 路线图

### 已完成

- **Multi-Action 单击 / 长按支持**：一个受支持的物理按键可以为单击和长按执行不同动作。
- **Generic Mouse Mode**：Windows 标准中键和侧键可以在不依赖 Logitech HID++ 的情况下使用 PourInput 动作；关闭后恢复原生中键点击和返回 / 前进行为。
- **基于设备能力的支持架构**：PourInput 可以根据检测到的设备能力开放或限制功能，而不是只依赖静态设备列表。

### 计划 / 未来方向

未来开发将重点探索 Enhanced Easy-Switch（增强型多设备切换）、Action Layers（操作层）以及更高级的 Multi-Action 工作流。

- **Enhanced Easy-Switch**：Easy-Switch（多设备切换）是 Logitech 提供的设备切换功能，可让支持的鼠标在已经配对的电脑或其他设备之间切换。Enhanced Easy-Switch 是 PourInput 未来计划探索的方向，目标是让用户更方便地在已连接的电脑之间切换，而不必只依赖鼠标原本的切换方式。它也可能成为未来跨设备工作流的基础。
- **Action Layers**：Action Layers 计划让同一个物理按键在不同操作层中执行不同功能。这样，即使鼠标按键数量有限，也可以通过切换操作层获得更多可用操作。
- **Advanced Multi-Action（高级多操作）**：Advanced Multi-Action 是现有单击与长按系统的未来扩展方向，目标是探索更丰富的按键交互和操作工作流。

这些内容是开发方向，不是已经完成的功能，也不是固定发布日期承诺。

## 贡献

欢迎提交文档改进、测试、设备信息、bug 修复和新设备支持。添加新设备前请阅读 [CONTRIBUTING_DEVICES.md](CONTRIBUTING_DEVICES.md)。开发说明见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 致谢

PourInput 基于原始 [Mouser](https://github.com/TomBadash/Mouser) 项目。感谢 Mouser 贡献者创建了让本项目成为可能的基础。

PourInput 将继续独立开发，同时尊重并致谢原始项目。

维护者：`pour-soi`

## License

本项目保留原始 Mouser 许可证。详见 [LICENSE](LICENSE)。
