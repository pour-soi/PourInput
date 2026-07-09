# PourInput v1.2.1 — Generic Mouse Status Fix

Release date: 2026-07-09

Repository: `pour-soi/PourInput`

Based on: `TomBadash/Mouser`

Maintainer: `pour-soi`

## English

PourInput v1.2.1 is a small patch release for the device status shown when Generic Mouse Mode is active.

Generic Mouse Mode functionality itself was already working: a standard mouse could use configured Generic Mouse Mode actions without a supported Logitech mouse. The issue was that the Mouse page status badge still reported the device as disconnected because it only reflected supported Logitech HID++ connection state.

This release keeps Logitech device detection separate from Generic Mouse Mode readiness:

- Supported Logitech device connected: `Connected — <device name>`
- No supported Logitech device and Generic Mouse Mode enabled: `Generic Mouse Mode Ready`
- No supported Logitech device and Generic Mouse Mode disabled: `No supported mouse detected`

Generic Mouse Mode still does not identify a specific physical standard mouse. It does not claim a standard mouse name or per-device identity.

No input, remapping, hook, blocking, button support, Logitech HID++, or localization-scope behavior changed in this release.

## 简体中文

PourInput v1.2.1 是一个小型补丁版本，修正通用鼠标模式启用时鼠标页面显示的设备状态。

通用鼠标模式本身此前已经可以正常工作：即使没有受支持的 Logitech 鼠标，普通鼠标也可以通过通用鼠标模式使用已配置的操作。问题在于鼠标页面的状态标签只反映受支持 Logitech HID++ 设备的连接状态，因此会误显示为未连接。

此版本将 Logitech 设备连接状态与通用鼠标模式就绪状态分开显示：

- 已连接受支持的 Logitech 设备：`已连接 — <device name>`
- 没有受支持的 Logitech 设备，但已启用通用鼠标模式：`通用鼠标模式已就绪`
- 没有受支持的 Logitech 设备，且未启用通用鼠标模式：`未检测到受支持的鼠标`

通用鼠标模式仍然不会识别某一只具体的普通鼠标，也不会显示虚构的标准鼠标名称或物理设备身份。

此版本没有改变输入、重映射、鼠标钩子、事件阻止、按键支持、Logitech HID++ 或本地化范围。

## Release Policy

Windows remains the only official release target for v1.2.1.

The public GitHub Release should contain only:

- `PourInput-v1.2.1-Windows.zip`
- `pourinput-v1.2.1-update.json`

macOS and Linux CI/build validation may remain, but public macOS and Linux release packages are not part of the official v1.2.1 release.

## Validation

This patch release is covered by focused tests for:

- Backend device status states.
- Generic Mouse Mode status transitions.
- Locale manager translations.
- QML policy coverage for the status labels.
- Update/version behavior.

## Known Limitations

- Windows remains the only official release target.
- Generic Mouse Mode is Windows-only.
- Generic Mouse Mode supports Middle Button, Side Button 1, and Side Button 2 only.
- Generic Mouse Mode cannot currently distinguish multiple standard mice by physical source device.
- Device support still depends on firmware, operating system exposure, and HID++ features.
