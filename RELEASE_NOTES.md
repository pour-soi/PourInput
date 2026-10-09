# PourInput v1.5.0 — UI refinement / 界面优化

## 中文

本次 Windows 更新优化鼠标配置、阅读和设置界面的信息层级与可读性。

- 主导航按鼠标、阅读、设置排列。应用配置选择移至鼠标页顶部，保留已有配置及自动切换行为。
- 调整设备、电量、通用鼠标模式和鼠标热点标签的展示，增大主要文字与动作控件，改善中英文阅读体验。
- 大窗口并排展示鼠标图与动作编辑器，较窄窗口恢复上下布局；普通窗口尺寸在下次启动时恢复。
- 动作浏览器一次仅显示一个分类，并自动定位当前动作所属分类。单击与长按、水平滚动左与右分别编辑，互不覆盖。
- 阅读页按书籍、阅读、浮窗外观和控制分区，简化帮助入口；保留 TXT/EPUB、章节、阅读位置、自动滚动和隐藏/显示行为。
- 优化设置页布局及 Windows 中文字体回退。

现有动作 ID、配置/映射和阅读数据格式保持兼容，无需迁移。窗口尺寸单独保存，不改变原有配置格式。隔离 UI 测试启动器仅用于开发验证，不是正式程序的启动入口。

验证：源码 UI 已通过隔离实机验证；自动测试共 934 项，917 项通过，17 项因平台或权限限制跳过。Windows 便携候选包已在干净沙盒中成功启动，校验和、更新清单与内嵌构建信息一致。沙盒启动检查不包含真实鼠标功能验证。

本次仅提供 Windows x64 便携版，程序未签名。使用时先从托盘退出旧实例，完整解压 ZIP，再运行 PourInput/PourInput.exe。正式程序使用正常用户配置；开发用隔离启动器的保护不会自动应用于正式 EXE。

## English

This Windows update improves the hierarchy and readability of Mouse, Reading, and Settings.

- Order navigation as Mouse, Reading, Settings. Move application-profile selection to the top of the Mouse page while preserving stored profiles and automatic switching.
- Refine device and battery information, Generic Mouse Mode, and hotspot labels. Enlarge primary text and action controls for English and Chinese.
- Place the Mouse Map beside the action editor on wide windows and stack them on narrower windows. Restore the normal window size on the next launch.
- Show one action category at a time and automatically select the category of the assigned action. Edit Click / Long Press and Scroll Left / Scroll Right independently.
- Organize Reading into Book, Reading, Panel Appearance, and Controls with compact inline help. Preserve TXT/EPUB, chapters, reading position, auto-scroll, and hide/show behavior.
- Refine Settings layout and Windows Chinese font fallback.

Existing action IDs, configuration/mapping formats, and Reading data formats remain compatible without migration. Window dimensions use a separate file. The isolated UI launcher is developer validation infrastructure, not the production entry point.

Validation: the source UI passed isolated real-machine testing. Of 934 automated tests, 917 passed and 17 were skipped for platform or permission limitations. The Windows portable candidate started successfully in a clean sandbox; its checksum, update manifest, and embedded build identity matched. The sandbox startup check does not validate physical mouse functionality.

This release targets Windows x64 only and the executable is unsigned. Exit the previous instance from its tray menu, extract the complete ZIP, then run PourInput/PourInput.exe. The production application uses normal user configuration; the developer launcher's isolation protections do not automatically apply to the packaged executable.
