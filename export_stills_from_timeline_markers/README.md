# Export Stills from Timeline Markers

Automatically export still frames from all markers in selected timelines. Stills are captured to a temporary Gallery album and exported with customizable formats.

**Key Features:**
- Export stills at every marker position in selected timelines
- Automatic naming: Timeline name + timecode (HH-MM-SS-FF)
- Four export formats: JPEG, PNG, TIFF, DPX
- Gallery-based workflow with automatic still labeling
- Temporary album (automatically cleaned up after export)
- Works in both Studio (UI dialog) and Free (console mode) versions

---

## Overview

This script automates the process of exporting still frames from timeline markers. Instead of manually positioning the playhead at each marker and grabbing stills, the script:

1. Scans selected timelines for all markers
2. Captures stills to a temporary Gallery album
3. Names stills using timeline name and timecode
4. Exports stills with your chosen format
5. Cleans up the temporary album

**Use Cases:**
- Create reference images from edit markers
- Export keyframes for VFX review
- Generate thumbnails for scene markers
- Create frame-accurate stills for color matching
- Export stills for client review

---

## Requirements

- DaVinci Resolve 16.2.0 or later
- DaVinci Resolve Studio (for UI dialog) or Free (console mode)
- Python 3.10
- Python `timecode` module (for timecode calculations)
- Selected timeline items in Media Pool

---

## Installation

### Install Python timecode Module

```bash
/usr/local/bin/python3.10 -m pip install timecode
```

### Manual Installation

Copy script to Resolve's Scripts folder:

**Mac:**
```bash
mkdir -p ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
cp export_stills_from_timeline_markers.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
```

**Windows:**
```cmd
mkdir "%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"
copy export_stills_from_timeline_markers.py "%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
```

**Linux:**
```bash
mkdir -p ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
cp export_stills_from_timeline_markers.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
```

### Accessing in Resolve

1. Restart DaVinci Resolve (if running during installation)
2. Go to: **Workspace → Scripts → Edit → export_stills_from_timeline_markers**
3. Select timeline items in Media Pool
4. Run the script

---

## Usage

### From Resolve Menu (Studio - UI Dialog)

1. **Select Timelines in Media Pool:**
   - Open the **Media Pool** panel
   - Select one or more **timeline items** (NOT clips!)
   - Timelines appear as stacked film strips in Media Pool

2. **Run the Script:**
   - Go to **Workspace → Scripts → Edit → export_stills_from_timeline_markers**
   - The configuration dialog will appear

3. **Configure Settings:**
   - **Export Format:** Choose export format (JPEG, PNG, TIFF, DPX)
   - **Export Folder:** Click "Browse..." to select output folder

4. **Export:**
   - Click **Export** to start the export process
   - Status label shows progress and results
   - Stills are exported to the selected folder
   - Files will be named: `TimelineName_HH-MM-SS-FF.ext`

5. **Close:**
   - Click **Close** when finished

### From Resolve Menu (Free - Console Mode)

If UIManager is not available (Resolve Free), the script runs in console mode:

1. Select timeline items in Media Pool
2. Run the script from **Workspace → Scripts**
3. Follow console prompts:
   - Select export format (1-4)
   - Enter export folder path
4. Script executes and shows results in console

### From Terminal

```bash
python3.10 export_stills_from_timeline_markers.py
```

Follow the same workflow as console mode above.

---

## Naming Convention

Stills are automatically named using the timeline name and record timecode.

**Format:** `{Timeline_Name}_{Record_Timecode}.{ext}`

**Example:**
- Timeline: "Main Edit"
- Marker at: 01:00:30:15
- Result: `Main_Edit_01-00-30-15.png`

**Notes:**
- Timeline name spaces are replaced with underscores
- Timecode uses hyphens instead of colons for filename compatibility
- Timecode respects timeline start timecode setting
- Each marker position generates one still file

---

## Export Formats

### JPEG (.jpg)
- **Best for:** General purpose, small file size
- **Compression:** Lossy
- **Use Cases:** Reference images, thumbnails, client review
- **Color Depth:** 8-bit

### PNG (.png)
- **Best for:** Lossless quality, transparency support
- **Compression:** Lossless
- **Use Cases:** Graphics, overlays, high-quality stills
- **Color Depth:** 8-bit from Resolve.

### TIFF (.tiff)
- **Best for:** High-quality archival, print work
- **Compression:** Lossless or uncompressed
- **Use Cases:** VFX plates, color grading reference, archival
- **Color Depth:** 16-bit

### DPX (.dpx)
- **Best for:** Professional VFX and film workflows
- **Compression:** Uncompressed or log-compressed
- **Use Cases:** VFX delivery, film scanning, high-end color work
- **Color Depth:** 10-bit, 12-bit, or 16-bit (need to verify Resolve's output)

**Recommendation:** Use JPEG for general reference, PNG for graphics/overlay work, TIFF for color-critical work, and DPX for professional VFX workflows.

---

## Workflow Examples

### Example 1: Export Scene Reference Stills as JPEG

**Scenario:** You've marked each scene in your timeline with Blue markers and want to export reference stills for each scene.

**Steps:**
1. Select timeline in Media Pool
2. Run script
3. Choose format: **JPEG**
4. Select export folder
5. Click **Export**

**Result:**
```
/export/folder/
├── Main_Edit_00-00-00-00.jpg  (Scene 1)
├── Main_Edit_00-05-12-10.jpg  (Scene 2)
├── Main_Edit_00-10-30-05.jpg  (Scene 3)
└── ...
```

---

### Example 2: Export VFX Plates as TIFF

**Scenario:** Your VFX team marked all shots requiring VFX work. You need to export high-quality stills.

**Steps:**
1. Select timeline in Media Pool
2. Run script
3. Choose format: **TIFF**
4. Select export folder
5. Click **Export**

**Result:**
```
/vfx/plates/
├── VFX_Timeline_01-00-30-15.tiff
├── VFX_Timeline_01-05-10-20.tiff
├── VFX_Timeline_01-10-05-00.tiff
└── ...
```

---

### Example 3: Export Multiple Timelines as PNG

**Scenario:** You have multiple versions of the edit (v1, v2, v3) and want to export all marked frames from all versions.

**Steps:**
1. Select all timeline items in Media Pool (Shift+Click or Cmd+Click)
2. Run script
3. Choose format: **PNG**
4. Select export folder
5. Click **Export**

**Result:**
```
/export/folder/
├── Edit_v1_00-01-00-00.png
├── Edit_v1_00-05-30-10.png
├── Edit_v2_00-01-05-00.png
├── Edit_v2_00-05-35-15.png
├── Edit_v3_00-01-10-00.png
└── ...
```

---

### Example 4: Export DPX for Film Workflow

**Scenario:** Creating DPX stills for film scanning workflow or high-end VFX delivery.

**Steps:**
1. Select timeline in Media Pool
2. Run script
3. Choose format: **DPX**
4. Select export folder
5. Click **Export**

**Result:** Uncompressed DPX files with timeline names and timecodes for frame identification.

---

## How It Works

### Gallery-Based Workflow

The script uses DaVinci Resolve's Gallery system to capture and export stills:

1. **Create Temporary Album:**
   - Creates a Gallery still album named "TempMarkerStills"
   - Used to hold captured stills during processing

2. **Capture Stills:**
   - For each marker in each selected timeline:
     - Sets timeline as current
     - Moves playhead to marker position
     - Calls `gallery.GrabStill()` to capture frame
     - Stores still object and generated filename

3. **Label Stills:**
   - For each captured still:
     - Uses `album.SetLabel(still, filename)` to set still's label
     - Label becomes the base filename for export (without extension)

4. **Export Stills:**
   - For each labeled still:
     - Calls `album.ExportStills([still], folder, "", format)`
     - Format parameter adds appropriate extension
     - Result: `{label}.{ext}` (e.g., "Main_Edit_01-00-30-15.png")

5. **Cleanup:**
   - Deletes all stills newly created stills from temporary album
   - Album itself remains

**Key Insight:** By setting the still's label in the Gallery, that label becomes the export filename base. The export format parameter adds the extension.

### Marker Scanning

- `timeline.GetMarkers()` returns dictionary: `{frame_id: marker_data}`
- Frame IDs are sorted to process markers in timeline order
- Each marker's frame_id is used to position playhead and capture still

### Timecode Conversion

- Uses Python `timecode` module for frame-to-timecode conversions
- Frame numbers are converted to "HH:MM:SS:FF" format
- Colons are replaced with hyphens for filename compatibility: "HH-MM-SS-FF"
- Handles variable frame rates correctly

---

## Technical Details

### API Methods Used

**Gallery Operations:**
```python
gallery = project.GetGallery()
album = gallery.GetCurrentStillAlbum()
still = gallery.GrabStill()                    # Capture current frame
album.SetLabel(still, "filename")              # Set still label (export name)
album.ExportStills([still], folder, "", "png") # Export with format
album.DeleteStills([still])                    # Delete still
```

**Timeline Operations:**
```python
timeline.GetMarkers()                    # Returns {frame_id: marker_data}
timeline.SetCurrentTimecode("01:00:30:15")  # Position playhead
timeline.GetCurrentVideoItem()           # Get clip at playhead position
```

**Marker Data Structure:**
```python
marker_data = {
    "color": "Blue",           # Marker color
    "name": "Scene 1",         # Marker name
    "note": "Wide shot",       # Marker note
    "duration": 1,             # Marker duration in frames
    "customData": "",          # Custom metadata
}
```

### Timecode Calculations

```python
from timecode import Timecode

# Convert frame to timecode
frame_rate = 23.976
frame_number = 1000
tc = Timecode(frame_rate, frames=frame_number)
print(tc)  # "00:00:41:16"

# Filename-safe format
tc_str = str(tc).replace(":", "-")  # "00-00-41-16"
```

### Gallery Still Naming

**Critical Pattern:**
```python
# Generate filename WITHOUT extension
filename = "Main_Edit_01-00-30-15"  # No .png, .jpg, etc.

# Set as still label
album.SetLabel(still, filename)

# Export with format - label becomes base, format adds extension
album.ExportStills([still], folder, "", "png")

# Result: Main_Edit_01-00-30-15.png
```

**Why This Works:**
- `SetLabel()` sets the still's internal name/label
- `ExportStills()` uses the label as the base filename
- Format parameter ("png", "jpg", etc.) adds the appropriate extension
- No need to manually construct full filename with extension

---

## Troubleshooting

### "No items selected in Media Pool"
- Make sure you've selected timeline items in the **Media Pool** (not Edit page timeline)
- Timeline items appear as stacked film strips in Media Pool bins

### "No timelines found in selected items"
- You selected regular clips instead of timelines
- Select timeline items (they have a different icon than media clips)

### "No markers found in selected timelines"
- Selected timelines don't have any markers
- Add markers to timelines (M key in Edit page)

### "Failed to capture still at frame X"
- Playhead may be at an invalid position
- Timeline may have gaps or no video at marker position
- Check that video tracks exist at marker positions

### "Failed to export still"
- Export folder may not be writable
- Disk may be full
- Check folder permissions

### Export folder is empty after running
- Check console output for errors
- Verify export format is supported
- Ensure Gallery has permission to write to folder

### Dialog doesn't appear (Free version)
- UIManager is not available in Resolve Free
- Script automatically falls back to console mode
- Follow console prompts to complete export

---

## Known Limitations

### Gallery Album Deletion
- Gallery albums cannot be deleted via API
- Script deletes stills from temporary album but album itself remains
- Empty album can be manually deleted from Gallery if desired

### Marker Types
- Script exports stills from all markers regardless of color or type
- To export only specific markers, pre-filter markers in timeline
- Future enhancement: Add marker color filtering

---

## Tips and Best Practices

### 1. Use Meaningful Marker Names
Marker names are not used in export filenames, but help identify what will be exported during preview.

### 2. Choose Format Based on Use Case
- **Quick reference:** JPEG
- **Graphics/web:** PNG
- **Color critical:** TIFF
- **VFX/film:** DPX

### 3. Organize Export Folders
Create subfolders for different timeline versions or formats:
```
/project/stills/
├── edit_v1/
├── edit_v2/
└── vfx_plates/
```

### 4. Preview Before Export
Always click **Preview** first to verify:
- Correct number of markers detected
- Timelines are selected properly
- No unexpected timelines included

### 5. Batch Multiple Timelines
Select multiple timelines at once to export all markers in one operation.

### 6. Verify Timecode Format
Exported filenames use "HH-MM-SS-FF" format (hyphens, not colons) for filesystem compatibility.

### 7. Check Disk Space
TIFF and DPX formats can be large (10-50 MB per still). Ensure adequate disk space before exporting many stills.

---

## Future Enhancements

Potential features for future versions:

- [ ] Filter markers by color (export only Blue markers, etc.)
- [ ] Filter markers by name pattern (regex support)
- [ ] Custom filename templates with variables
- [ ] Batch export to multiple formats simultaneously
- [ ] Progress bar for long exports
- [ ] Thumbnail preview of stills before export
- [ ] Export metadata file with marker info (JSON, CSV)
- [ ] Automatic subfolder creation by marker color
- [ ] Option to keep Gallery album instead of deleting

---

## See Also

- [Add LUTs by Rules](../add_luts_by_rules/) - Automatic LUT application by properties
- [Batch Edit Script](../batch_edit/) - Component-based clip renaming
- [Find and Replace](../Find_and_Replace/) - Timeline search and replace
- [Setup Guide](../MACOS_SETUP_GUIDE.md) - Environment configuration

---

## Support

For issues or questions:
- Check the main repository [README](../README.md)
- Ensure environment is set up correctly (see [Setup Guide](../MACOS_SETUP_GUIDE.md))
- Verify `timecode` module is installed: `python3.10 -m pip list | grep timecode`
