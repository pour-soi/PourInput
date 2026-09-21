# Reading Mode

Reading is a Windows feature above mouse routing. It does not use the active
mouse profile or change Generic/MX mappings.

- Open the Reading page, import a local TXT/EPUB, then enable Reading Mode.
- Wheel up selects the previous page; wheel down selects the next.
- 120 accumulated wheel units trigger one step. Further events in the burst
  remain consumed. A 250 ms quiet interval rearms navigation.
- Normal shows the document title and supports dragging. Minimal and Ghost
  pass mouse clicks through. All presentations are borderless, topmost, and
  non-focusable. The overlay has no transient settings-window owner.
- Hold-to-hide observes a selected key or standard Windows mouse button.
  The control retains its existing action. Hiding changes visibility only:
  reading stays enabled and wheel navigation remains active.

## Storage and import

Reader files live under the application's configuration directory in reader/.
state.json holds only enabled state, document reference, current group index,
display mode, opacity, and hide key. Text groups live in
documents/<content-hash>.json; full book text never enters config.json.
Imports are retained locally, so the current document works after the source
file moves. Importing another document starts that document at group zero.
Startup restores the current document and group. No profile or device switch
resets them. Corrupt reader files are reported and preserved.

TXT accepts UTF-8 (with or without BOM), BOM-marked UTF-16, and GB18030.
EPUB follows the package spine and ignores head/script/style text. It does not
fetch links, extract archive paths onto disk, or render book HTML. DRM-protected
EPUBs are not supported. Input files are limited to 32 MB and EPUB text reads
to 64 MB. Groups contain up to three punctuation-delimited sentences and at
most 600 characters; very long passages are divided to fit.

## Verification and remaining physical checks

Automated tests cover state persistence, failed/corrupt imports, EPUB order,
grouping, burst filtering, queued-event invalidation, profile/Generic changes,
hold visibility invariants, and the Windows hook's suppression behavior.
Qt tests inspect window flags and load both QML components. Offscreen renders
use synthetic text.

Real MX/standard-mouse wheel feel, focus retention, desktop click-through,
topmost behavior, and hold/release timing still require desktop/hardware
validation. No live input engine was started for these tests. Wheel interception
and global hold observation are currently Windows-only.


## v1.4.0 pagination

The panel keeps the selected size and font. Qt text layout fills successive pages across stored text groups; only the last page may be short. A group index and character offset persist the reading anchor. Default height is 240 px; minimum height fits one line. Reader data stays under the separate local reader directory.
