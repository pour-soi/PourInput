# Mouser Multi-Action

**One Button. Two Actions.**

Mouser Multi-Action 是 [TomBadash/Mouser](https://github.com/TomBadash/Mouser) 的开源分支，重点加入通用的 Multi-Action Button 框架。

支持的鼠标按键可以分别设置：

- **Click Action**：短按动作
- **Long Press Action**：长按动作

当前版本：`v0.1.0`

仓库：`pour-soi/Mouser-Multi-Action`

## 项目目标

Mouser Multi-Action 让一个支持的鼠标按键承担两个独立动作。例如：

- Back：短按返回，长按复制
- Forward：短按前进，长按粘贴
- Mode Shift：短按截图到剪贴板，长按切换滚轮模式

默认长按阈值为 300 ms。

## 功能

- 通用 Multi-Action Button 框架
- 支持 Click 和 Long Press
- 支持 Mode Shift、Back Button、Forward Button
- 通用分发器，避免每个按键重复实现计时逻辑
- 配置迁移
- 新 UI 字段：Click Action 和 Long Press Action
- Mode Shift HID++ diversion 同步
- 版本化 Windows 发布包

## 安装

1. 打开 [最新 Release 页面](https://github.com/pour-soi/Mouser-Multi-Action/releases/latest)。
2. 下载 `Mouser-Multi-Action-v0.1.0-Windows.zip`。
3. 解压 zip。
4. 运行 `Mouser-Multi-Action-v0.1.0/Mouser.exe`。

如果已经运行其他 Mouser 或 Mouser Multi-Action 构建，请先从系统托盘退出。

## 使用

打开 Mouse 页面，选择支持的按键，然后分别配置：

- Click Action
- Long Press Action

短于 300 ms 的按压会执行 Click Action。按住至少 300 ms 后松开会执行 Long Press Action。

如果没有配置 Long Press Action，该按键会保持当前 Mouser Multi-Action 的默认行为。

## 支持设备

Mouser Multi-Action 面向本应用可以检测和控制的 Logitech HID++ 鼠标。

Multi-Action 当前启用的按键：

- Mode Shift
- Back Button
- Forward Button

实际可用性取决于设备通过 HID++ 暴露的控制能力。某些按键需要是 reprogrammable 和 divertable，Mouser Multi-Action 才能拦截。

如果你的设备缺少按键支持，请在 GitHub issue 中附上 Mouse 页面复制出的 device info JSON。

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

构建 Windows 包：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller Mouser.spec --noconfirm
```

## 打包发布

```powershell
.\scripts\create_release.ps1 -Version v0.1.0
```

输出文件：

```text
release/
    Mouser-Multi-Action-v0.1.0-Windows.zip
    RELEASE_NOTES-v0.1.0.md
    CHANGELOG.md
```

## 路线图

### v0.2.0

- Double Click support
- Custom Long Press timeout

### v0.3.0

- Per-button timeout
- Export/Import configuration

### v0.4.0

- Macro support
- Sequential actions

### v1.0.0

- Stable release

## 贡献

欢迎提交文档改进、测试、设备信息、Bug 修复和新设备支持。

添加新设备前请阅读 [CONTRIBUTING_DEVICES.md](CONTRIBUTING_DEVICES.md)。

开发说明见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 致谢

Mouser Multi-Action 基于 [TomBadash/Mouser](https://github.com/TomBadash/Mouser)。

维护者：`pour-soi`

## License

本项目保留原 Mouser 许可证。详见 [LICENSE](LICENSE)。
