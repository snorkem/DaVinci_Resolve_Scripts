# Batch Edit - Component-Based Clip Renaming

Build new clip names from scratch by chaining components together. A flexible, modular approach to batch renaming clips in DaVinci Resolve.

**Key Feature:** Build names using any combination of counters, custom text, and clip data - no manual typing required!

---

## Overview

Instead of find-and-replace operations, this script builds entirely new names by combining "components" in sequence. Each component generates a piece of the final name.

**Example:**
- Component 1: Specified Text → `"Scene_"`
- Component 2: Counter (start: 10, padding: 3) → `"010"`
- Component 3: Specified Text → `"_"`
- Component 4: Column Data (Clip Color) → `"Orange"`
- **Result:** `Scene_010_Orange`

---

## Supported Components

### 1. Counter

Generates sequential numbers for each clip.

**Parameters:**
- **Start:** Starting number (default: 1)
- **Padding:** Number of digits with zero-padding (default: 3)
  - Padding 3: `001`, `002`, `003`
  - Padding 4: `0001`, `0002`, `0003`
- **Increment:** Step size between numbers (default: 1)
  - Increment 1: `001`, `002`, `003`
  - Increment 5: `005`, `010`, `015`
  - Increment 10: `010`, `020`, `030`

**Example Output:**
- Start 1, Padding 3, Increment 1: `001`, `002`, `003`, ...
- Start 100, Padding 4, Increment 10: `0100`, `0110`, `0120`, ...

### 2. Specified Text

Inserts custom text exactly as typed.

**Parameters:**
- **Text:** The text to insert (any string)

**Use Cases:**
- Prefixes: `"A-Cam_"`
- Separators: `"_"`, `"-"`, `"."`
- Suffixes: `"_FINAL"`
- Keywords: `"Interview"`, `"Broll"`

**Example Output:**
- Text = `"Scene_"`: Always outputs `Scene_`
- Text = `"_"`: Always outputs `_`

### 3. Column Data

Pulls data from clip properties or metadata.

**Available Columns:**
- **Name:** Current clip name
- **Clip Color:** Clip color marker (Orange, Blue, etc.)
- **Metadata Fields:** Any metadata field (Scene, Shot, Take, Camera, etc.)

**Use Cases:**
- Preserve part of original name
- Add clip color to filename
- Include custom metadata in name

**Example Output:**
- Column = "Clip Color", Value = Orange: `Orange`
- Column = "Scene", Value = INT_OFFICE: `INT_OFFICE`

---

## Usage

### Running the Script

**From Terminal:**
```bash
python3.10 batch_edit.py
```

**From Resolve:**
1. Select clips in the **Media Pool** (not timeline!)
2. Go to: **Workspace → Scripts → batch_edit**
3. Configure components
4. Click **Preview** to see results
5. Click **Apply** to rename clips

### Requirements
- DaVinci Resolve Studio (for UI dialogs)
- Select clips in Media Pool before running
- Works on Media Pool clips, not timeline clips

---

## Workflow Examples

### Example 1: Simple Sequential Numbering

**Goal:** Rename clips to `001`, `002`, `003`, etc.

**Components:**
1. Counter: Start=1, Padding=3, Increment=1

**Result:**
```
Original        → New
IMG_1234.mov    → 001
IMG_1235.mov    → 002
IMG_1236.mov    → 003
```

---

### Example 2: Scene Prefix with Counter

**Goal:** Rename clips to `Scene_001`, `Scene_002`, etc.

**Components:**
1. Specified Text: `Scene_`
2. Counter: Start=1, Padding=3, Increment=1

**Result:**
```
Original        → New
A001_C001.mov   → Scene_001
A001_C002.mov   → Scene_002
A001_C003.mov   → Scene_003
```

---

### Example 3: Camera + Counter + Clip Color

**Goal:** Rename clips to `A-Cam_010_Orange`, `A-Cam_011_Blue`, etc.

**Components:**
1. Specified Text: `A-Cam_`
2. Counter: Start=10, Padding=3, Increment=1
3. Specified Text: `_`
4. Column Data: Clip Color

**Result:**
```
Original        → New
IMG_1234.mov    → A-Cam_010_Orange
IMG_1235.mov    → A-Cam_011_Blue
IMG_1236.mov    → A-Cam_012_Orange
```

*(Assumes clips are marked with Orange and Blue clip colors)*

---

### Example 4: Preserve Original Name + Counter

**Goal:** Keep original filename and add counter suffix: `IMG_1234_001`

**Components:**
1. Column Data: Name
2. Specified Text: `_`
3. Counter: Start=1, Padding=3, Increment=1

**Result:**
```
Original        → New
IMG_1234.mov    → IMG_1234.mov_001
IMG_1235.mov    → IMG_1235.mov_002
IMG_1236.mov    → IMG_1236.mov_003
```

---

### Example 5: Metadata-Based Naming

**Goal:** Build names from metadata: `Scene101_TakeA_001`

**Assumptions:** Clips have metadata fields "Scene" and "Take"

**Components:**
1. Column Data: Scene
2. Specified Text: `_`
3. Column Data: Take
4. Specified Text: `_`
5. Counter: Start=1, Padding=3, Increment=1

**Result:**
```
Original        → New
A001.mov        → Scene101_TakeA_001
A002.mov        → Scene101_TakeB_002
B001.mov        → Scene102_TakeA_003
```

---

### Example 6: Skip Numbering (Every 10th)

**Goal:** Number clips as 10, 20, 30 for rough organization.

**Components:**
1. Specified Text: `Clip_`
2. Counter: Start=10, Padding=3, Increment=10

**Result:**
```
Original        → New
IMG_1234.mov    → Clip_010
IMG_1235.mov    → Clip_020
IMG_1236.mov    → Clip_030
```

---

## Dialog Interface

The batch edit dialog provides:

### Component Rows (Up to 10)
Each row contains:
- **Enable Checkbox:** Turn component on/off
- **Component Type Dropdown:** Choose Counter, Specified Text, or Column Data
- **Component Parameters:** Changes based on type selected
  - Counter: Start, Padding, Increment fields
  - Specified Text: Text entry field
  - Column Data: Column dropdown (Name, Clip Color, metadata)

### Preview Section
Shows before/after for all selected clips:
```
Original Name → New Name
IMG_1234.mov → Scene_001_Orange
IMG_1235.mov → Scene_002_Blue
...
```

### Action Buttons
- **Preview:** Generate preview without applying changes
- **Apply:** Rename all clips with configured components
- **Close:** Exit without changes

---

## Component Chaining

Components are applied in **sequence** from top to bottom. Each component adds to the result:

**Example Chain:**
```
Component 1: "Interview_"
  Result: "Interview_"

Component 2: Counter (001)
  Result: "Interview_001"

Component 3: "_"
  Result: "Interview_001_"

Component 4: Column Data (Clip Color = "Orange")
  Result: "Interview_001_Orange"

Final Name: Interview_001_Orange
```

**Key Points:**
- Components execute in order (Row 1 → Row 2 → Row 3, etc.)
- Each component adds to the growing name
- Disabled components (unchecked) are skipped
- If no components produce output, original name is kept

---

## Key Concepts

### Media Pool vs Timeline

**Important:** This script operates on **Media Pool clips**, not timeline instances.

- ✅ **Media Pool:** Source clips in bins/folders
- ❌ **Timeline:** Clip instances on the timeline

Renaming Media Pool clips affects the source, which updates all timeline instances of that clip automatically.

### Component vs Find/Replace

**Find/Replace:**
- Good for: Changing part of existing names
- Example: Replace "A-Cam" with "B-Cam"

**Component-Based (This Script):**
- Good for: Building entirely new names from scratch
- Example: Create "Scene_001_Orange" from "IMG_1234.mov"

### Metadata Requirements

To use **Column Data** with metadata fields:
1. Clips must have the metadata field populated
2. Empty metadata fields produce empty strings in the component
3. Use `test_clip_properties.py` (in Find_and_Replace folder) to see available metadata

---

## Installation

### Quick Install (Recommended)

From repository root:
```bash
./install_scripts.sh
```

### Manual Installation

**Mac:**
```bash
mkdir -p ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
cp batch_edit.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
```

**Windows:**
```cmd
mkdir "%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"
copy batch_edit.py "%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
```

**Linux:**
```bash
mkdir -p ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
cp batch_edit.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
```

### Accessing in Resolve

1. Restart DaVinci Resolve (if running during installation)
2. Go to: **Workspace → Scripts → Edit → batch_edit**
3. Select clips in Media Pool
4. Run the script

---

## Troubleshooting

### "No items selected"
- Select clips in the **Media Pool** before running the script
- You must select source clips, not timeline instances

### "ERROR: Could not connect to DaVinci Resolve"
- Ensure DaVinci Resolve is running
- Ensure a project is open
- Try restarting Resolve

### "No components configured"
- At least one component must be enabled (checkbox checked)
- Configure component parameters before applying

### Column Data shows empty values
- The clip may not have that property/metadata field
- Use `test_clip_properties.py` to verify available fields
- Metadata fields must be populated before use

### Dialog doesn't appear (Free version)
- UI dialogs require DaVinci Resolve Studio
- The Free version does not support UIManager
- Script will not work in Free version without console mode implementation

### Names don't change on timeline
- You renamed the Media Pool clip successfully
- Timeline instances should reflect the change automatically
- Try refreshing the timeline view (F5) if needed

---

## Tips and Best Practices

### 1. Always Preview First
- Click **Preview** before **Apply** to see results
- Verify the pattern looks correct for all clips
- Check for empty components or missing metadata

### 2. Use Separators
Add separators between components for readability:
- Underscores: `_`
- Hyphens: `-`
- Periods: `.`

**Good:** `Scene_001_Orange`
**Bad:** `Scene001Orange`

### 3. Consistent Padding
Use consistent padding for counters to maintain sort order:
- ✅ Padding 3: `001`, `002`, ..., `010`, ..., `100`
- ❌ No padding: `1`, `2`, ..., `10`, ..., `100` (sorts incorrectly)

### 4. Test on a Few Clips First
- Select 2-3 clips for testing
- Verify the naming pattern works
- Then apply to larger selections

### 5. Undo via History
- DaVinci Resolve does not have built-in undo for clip renaming
- Consider duplicating clips before batch renaming large sets
- Keep original names documented if needed for reference

---

## Technical Notes

### Component Architecture

The script uses an abstract base class pattern:

```python
class Component(ABC):
    """Abstract base class for name components."""

    @abstractmethod
    def generate(self, item: Any, index: int, previous_result: str) -> str:
        """Generate component output."""
        pass
```

Each component type implements `generate()`:
- **CounterComponent:** Generates sequential numbers
- **SpecifiedTextComponent:** Returns custom text
- **ColumnDataComponent:** Extracts clip properties/metadata

### API Methods Used

**Reading Clip Data:**
```python
name = item.GetName()                           # Current clip name
color = item.GetClipProperty("Clip Color")      # Clip color
metadata = item.GetMetadata()                   # All metadata fields
```

**Writing Clip Name:**
```python
result = item.SetName(new_name)                 # Returns True on success
```

### Inline Resolve Connection

Uses inline connection pattern (no external dependencies):
```python
def get_resolve() -> Any | None:
    """Get the DaVinci Resolve scripting API object."""
    add_resolve_module_path()
    import DaVinciResolveScript as dvr_script
    return dvr_script.scriptapp("Resolve")
```

Works in both terminal and Resolve menu contexts without environment variables.

---

## Comparison with Other Scripts

### batch_edit.py (This Script)
- **Purpose:** Build new names from components
- **Approach:** Additive - chain components together
- **Best For:** Creating systematic naming schemes
- **Use Case:** "I want all clips named `Scene_XXX_Color`"

### find_and_replace_selected.py
- **Purpose:** Find and replace text in existing names
- **Approach:** Substitution - replace one text with another
- **Best For:** Modifying part of existing names
- **Use Case:** "Change all `A-Cam` to `B-Cam`"

---

## See Also

- [Find and Replace Script](../Find_and_Replace/) - Find/replace in clip properties
- [Add LUTs by Rules](../add_luts_by_rules/) - Automatic LUT application by properties
- [DaVinci Resolve API Documentation](../API%20Docs/) - Complete API reference
- [Setup Guide](../MACOS_SETUP_GUIDE.md) - Environment configuration

---

## Development Notes

### Removed Features

**Change Case Component:** Previously included but removed for simplicity. If needed, implement as:
```python
class ChangeCaseComponent(Component):
    def generate(self, item: Any, index: int, previous_result: str) -> str:
        return previous_result.upper()  # or .lower(), .title()
```

### Future Enhancements

- [ ] Regex component for advanced text manipulation
- [ ] Date/time component for timestamps
- [ ] File extension component
- [ ] Random string component for unique IDs
- [ ] Conditional components (if/else logic)
- [ ] Save/load component presets
- [ ] Console mode for Resolve Free

---

## Support

For issues or questions:
- Check the main repository [README](../README.md)
- Ensure environment is set up correctly (see [Setup Guide](../MACOS_SETUP_GUIDE.md))
