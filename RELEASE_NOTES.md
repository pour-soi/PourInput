# PourInput v1.5.1 — Visual polish / 视觉优化

## English

This Windows update brings a more consistent, refined interface to the completed PourInput controls.

- Align Profile, device, and battery information in the Mouse header. Unify shared buttons, dropdowns, and numeric adjustments.
- Refine the single-category Action Browser and independent Click / Long Press and Scroll Left / Scroll Right editors. Arrange gesture directions in two columns when the editor has room.
- Improve Reading and Settings spacing and alignment. Group Panel Appearance controls in compact responsive columns.
- Add the approved transparent ivory-white Generic Mouse illustration, with accurately aligned Middle, Forward, and Back hotspots.
- Polish English and Simplified Chinese presentation and refresh translated Hide / Show Key labels after switching languages. Keep ordinary control and font sizes stable as the window resizes.
- Fix the empty Desktop directory setup in the isolated developer launcher used for validation.

Existing action IDs, mouse mappings, capability restrictions, profiles, configuration formats, and Reading data remain compatible. No migration is required.

The approved source UI passed isolated real-machine validation. Automated checks and the Windows workflow validate the release build; packaged startup checks do not replace physical mouse testing.

**Windows x64 portable edition; unsigned executable.** Exit the previous instance from its tray menu, extract the entire ZIP into a new folder, then run `PourInput/PourInput.exe`. The official app uses your normal configuration; it is separate from the isolated developer test launcher. The download includes a SHA-256 checksum and an update manifest. This release does not replace the separate macOS release.

## 简体中文

本次 Windows 更新统一并精修 PourInput 已有界面，让日常配置更清晰、协调。

- 对齐鼠标页顶部的配置、设备和电量信息，统一按钮、下拉框与数值调整控件。
- 优化单分类动作浏览器，保留单击／长按、水平滚动左／右的独立设置；手势编辑区域宽度足够时，以两列排列四个方向。
- 改善阅读和设置页的间距与对齐，将浮窗外观整理为紧凑、可响应窗口宽度的分组。
- 使用已确认的象牙白透明通用鼠标插画，准确对齐中键、前进、后退三个热点。
- 精修中英文显示，切换语言后及时刷新隐藏／显示按键的译名；调整窗口大小时保持普通控件与字体尺寸稳定。
- 修复隔离开发测试启动器的空 Desktop 目录创建，避免测试文件选择框提示路径不存在。

现有动作 ID、鼠标映射、设备能力限制、应用配置、配置格式和阅读数据保持兼容，无需迁移。

已确认的源码界面通过了隔离实机验证。自动检查与 Windows 工作流用于验证发布构建；安装包启动检查不等同于真实鼠标功能测试。

**Windows x64 便携版，程序尚未签名。** 请先从托盘退出旧实例，将完整 ZIP 解压到新文件夹，再运行 `PourInput/PourInput.exe`。正式程序使用正常用户配置，与隔离开发测试启动器分开。下载包含 SHA-256 校验文件和更新清单。本次不会替换独立的 macOS 版本。
