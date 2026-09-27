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
- Press the selected key or standard Windows mouse button to hide the panel.
  Releasing keeps it hidden; press again to show it. While reading is enabled,
  the selected mouse button is consumed; keyboard keys retain their usual action.
  Hiding changes visibility only:
  reading stays enabled and wheel navigation remains active.

## Storage and import

The Reading page offers a chapter selector. New TXT imports recognize standalone
Chinese chapter headings and English Chapter/Part/Book headings. EPUB imports use
EPUB 3 contents navigation or EPUB 2 NCX, including fragment targets; heading tags
are the fallback. Chapter metadata lives with the document, outside config.json.
Selecting a chapter saves its text anchor and pauses automatic scrolling without
changing Reading Mode, visibility, or wheel ownership. The panel starts at that
chapter's anchor, with matching title text on its own line. Pages continue from
that position using the fixed panel and font size, without the previous chapter's tail.
Older imports estimate chapters from retained text without rewriting the book or
moving its position. Their original EPUB contents and TXT line breaks are no
longer available; the UI recommends reimporting for more accurate recognition.

When no explicit contents or headings exist, new imports conservatively suggest
isolated short titles surrounded by blank lines and followed by a long prose
paragraph. At least two candidates are required. Suggested entries are labeled
and require confirmation before jumping; cancel leaves the position unchanged.
The inference flag is saved with chapter metadata. This heuristic can miss or
misidentify titles and is not applied to flattened legacy text. Reimport the
original file to use its line spacing. Explicit EPUB contents/headings take priority.

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
toggle visibility invariants, and the Windows hook's suppression behavior.
Qt tests inspect window flags and load both QML components. Offscreen renders
use synthetic text.

Real MX/standard-mouse wheel feel, focus retention, desktop click-through,
topmost behavior, and press/release toggle timing still require desktop/hardware
validation. No live input engine was started for these tests. Wheel interception
and global key observation are currently Windows-only.


## v1.4.0 pagination

The panel keeps the selected size and font. Qt text layout fills successive pages across stored text groups; only the last page may be short. A group index and character offset persist the reading anchor. Default height is 240 px; minimum height fits one line. Reader data stays under the separate local reader directory.

## Continuous auto-reading (v1.4.2)

The Reading page offers start/pause and a 5–100 px/s speed control in English and Simplified Chinese. Auto-reading uses the existing wrapped text lines, a clipped viewport, and fractional vertical movement, without changing panel or font size. Only visible lines plus a small buffer are rendered.

The reader store saves speed, text anchor, and fractional line position. Playback starts paused after restart. Position is checkpointed every two seconds and when pausing or closing; no document content is added to the mouse config. Hiding freezes motion without changing reading state or wheel ownership; pressing again to show the panel resumes from the same position. Reading OFF stops playback, and reaching the final visible text stops playback without disabling Reading Mode. Manual wheel navigation retains its existing ownership and resumes automatic movement from the selected position.
