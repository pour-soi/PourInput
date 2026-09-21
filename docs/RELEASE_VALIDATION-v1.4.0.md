# v1.4.0 validation

## Scope
Windows release from v1.3.5 commit 5f368ffd2ad48fc146a01898262c59d4f8ba6ac4, the exact forced-reconnect fix, and the accepted Reading Mode validation source. Remote-mouse and macOS accessibility experiments are excluded. The existing macOS release remains separate.

## Completed before publication
- User hardware acceptance with MX Master 4 and Zowie: reading on/off, Generic on/off, wheel burst control, topmost/no-focus/click-through, hold-to-hide and wheel ownership while hidden. Non-overlapping MX controls checked; long-duration hardware soak is not claimed.
- User accepted fixed-font continuous pages filling the panel after the last pagination fix.
- Windows full suite: 868 tests, 851 passed, 17 skipped. One skip is the host's missing symlink privilege; this Linux path test remains enabled in hosted Linux CI. Other skips are platform/optional-dependency conditions.
- The reconnect test now mocks only its own module clock; logging no longer exhausts its finite mocked timestamps. Runtime reconnect patch is unchanged.
- QML lint exits successfully, with existing-style unqualified-access warnings. Diff whitespace check passes.
- Reader/UI tests include actual Windows font metrics, all three modes, no-loss bidirectional pagination, saved character anchors, and independent hold/wheel state.
- Homepage captures use actual release QML and non-sensitive demo text, rendered offscreen with Fusion controls. They are UI illustrations, not evidence of real hardware events. Existing mouse screenshots are retained.

## Build and publication gates
Build from a clean committed tree. Verify embedded version/commit/dirty metadata, bundled reader QML/assets, ZIP checksum and update manifest. Publish a new immutable v1.4.0 tag only after main CI succeeds. Independently download the published assets and verify again; execution evidence is retained outside the source tree.

## Limits
Unsigned Windows executable. No new macOS/Linux Reading Mode hardware validation, no fresh full OS/DPI matrix, and no long-term reconnect soak. No code signing or installer is introduced.

## Local build environment

Use a short, isolated virtual environment and a minimal build PATH containing Python, Git, and Windows system directories. The developer tools PATH included Poppler ICU DLLs that PyInstaller incorrectly collected as Qt dependencies; the failed builds were retained and not published. The final build must not contain those unrelated ICU libraries. Queued HID observer tests explicitly drain their Qt metacalls before asserting visibility.
