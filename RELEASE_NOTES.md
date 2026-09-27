# PourInput v1.4.3 — Chapter navigation / 章节导航

## 中文

PourInput 是鼠标自定义软件。本次 Windows 更新完善附加的阅读功能，保留现有 Generic/MX 映射和设备增强功能。

- 隐藏键改为按一下隐藏、松开保持隐藏、再按一下显示。隐藏期间自动阅读暂停，显示后继续。
- 章节目录支持 EPUB 内置目录、TXT 章节标题。没有明确标题时，尝试根据短行与空行推测；推测结果会标注并要求确认。
- 章节跳转从标题开始，标题独占一行，不再带上上一章的尾句。字号和浮窗大小保持不变。
- 章节信息与阅读进度独立保存；重启后保留位置，自动阅读默认暂停。旧版导入的书籍可能需要重新导入以获得完整目录。

用户已验证章节跳转及重启位置恢复；自动检查覆盖隐藏状态、自动阅读、章节识别和鼠标路由。推测目录可能不完整或误判。请退出旧版托盘进程，将 ZIP 完整解压到短路径后运行 PourInput/PourInput.exe。本次仅发布 Windows，程序未签名。

## English

PourInput customizes mouse controls. This Windows update improves its optional reader while preserving Generic/MX mappings and device enhancements.

- Press once to hide, release keeps the panel hidden, and press again to show. Auto-reading pauses while hidden and resumes when shown.
- Navigate EPUB contents and recognized TXT chapter headings. When explicit headings are absent, layout-based suggestions are labeled and require confirmation.
- Chapter jumps start at the title on its own line, without the previous chapter's tail. Panel and font size remain fixed.
- Chapter metadata and reading progress remain in the independent reader store. Restart restores position with playback paused. Older imports may need reimporting for accurate contents.

The user verified chapter jumps and restart position recovery; automated checks cover visibility, auto-reading, chapter recognition, and mouse routing. Suggested chapters may be incomplete or incorrect. Quit the old tray process, fully extract the ZIP to a short path, then run PourInput/PourInput.exe. Windows only; unsigned executable.
