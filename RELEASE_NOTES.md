# PourInput v1.4.1 — Hide-button fix / 隐藏键冲突修复

## 中文

Windows 修复版本。阅读模式开启时，设为隐藏键的鼠标按键只控制浮窗，不再同时触发自定义动作或系统后退。关闭阅读模式后自动恢复原来的按键功能；按住途中关闭阅读，也不会在松开时补触发动作。

保留已保存的鼠标映射、阅读位置和隐藏期间的滚轮控制。用户已确认 Windows 实机测试正常。此修复针对鼠标隐藏键，键盘隐藏键不在本次变更范围内。

下载 ZIP 后解压到较短路径（例如 F:\Apps），退出旧版托盘进程，再运行 PourInput/PourInput.exe。不要在解压报错时跳过文件。原有设置保持不变。此版本未签名；macOS 和 Linux 不在本次发布范围内。

## English

Windows maintenance release. While Reading Mode is enabled, the configured mouse hide button exclusively hides/restores the panel instead of also executing a custom action or native Back. Disabling Reading Mode restores normal button actions; disabling it during a hold consumes the matching release.

Saved mappings, reading position, and wheel ownership while hidden are preserved. The user confirmed successful Windows hardware validation. This fix covers mouse hide buttons; keyboard hide keys are unchanged.

Extract the ZIP to a short path (for example F:\Apps), quit the old tray process, and run PourInput/PourInput.exe. Do not skip files if extraction reports an error. Existing settings are preserved. The executable is unsigned. No macOS or Linux release is included.
