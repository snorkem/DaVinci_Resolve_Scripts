# Add LUTs by Rules

Automatically apply LUTs to timeline clips based on property matching rules (codec, resolution, frame rate, clip color).

## Features

- **Automatic Property Discovery**: Scans selected timelines to discover available codecs, resolutions, frame rates, and clip colors
- **Dropdown-Only Interface**: No typing required - all options populated from actual timeline data
- **Multiple Rule Types**: Match by codec, resolution, frame rate, or clip color
- **Exact Matching**: Precise property matching for accurate LUT application
- **LUT Removal**: Remove existing LUTs from nodes using the "(None - Remove LUT)" option
- **Node Selection**: Specify which color node receives the LUT (1-10)
- **Preview Before Apply**: See which clips will be affected before making changes
- **Batch Processing**: Apply LUTs to multiple selected timelines at once
- **Works Both Contexts**: Run from terminal or Resolve's Workspace → Scripts menu

## Requirements

- DaVinci Resolve 16.2.0 or later
- DaVinci Resolve Studio (for UI dialog) or Free (console mode)
- Python 3.10
- Selected timeline items in Media Pool

## Usage

### 1. Select Timelines in Media Pool

In DaVinci Resolve:
1. Open the **Media Pool** panel
2. Select one or more **timeline items** (NOT clips!)
3. Run the script

**Important**: Only timeline items can be selected. If you select regular clips, you'll get an error.

### 2. Run the Script

**From Resolve Menu:**
- Go to **Workspace → Scripts → add_luts_by_rules**

**From Terminal:**
```bash
python3.10 add_luts_by_rules.py
```

### 3. Script Initialization

The script will:
1. Scan the **selected timelines** to discover:
   - Video codecs present (e.g., H.264, ProRes 422 HQ, DNxHD)
   - Resolutions (e.g., 3840x2160, 1920x1080)
   - Frame rates (e.g., 23.976, 24.000, 29.97)
   - Clip colors (e.g., Orange, Blue, Teal)

2. Scan for available LUTs in standard locations:
   - `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
   - `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/User/LUT/`

3. Show the configuration dialog

### 4. Configure Rules

In the dialog:

1. **Enable Rule**: Check the box to enable a rule
2. **Rule Type**: Choose what property to match:
   - **Codec**: Match by video codec
   - **Resolution**: Match by resolution (width x height)
   - **Frame Rate**: Match by frame rate
   - **Clip Color**: Match by clip color marker

3. **Value**: Select from dropdown of discovered values
   - Options are automatically populated from your project
   - Only shows values actually present in your timelines
   - Properties must match exactly

4. **LUT**: Select LUT file from dropdown
   - Shows all .cube, .3dl, .ilut, and .dat files in Resolve's LUT folders
   - Select "(None - Remove LUT)" to remove any existing LUT from the specified node

5. **Node**: Specify which color node receives the LUT (1-10, default: 1)

### 5. Preview & Apply

- Click **Preview** to see which clips will be affected
- Preview shows:
  - Timeline name
  - Clip name
  - Matched property value
  - LUT to be applied
- Click **Apply** to apply LUTs to all matching clips
- Status bar shows results (clips processed, LUTs applied, errors)

## Example Workflows

### Example 1: Apply Different LUTs for Different Codecs

**Scenario**: You have footage from multiple cameras with different codecs and want to apply appropriate conversion LUTs.

**Steps**:
1. Select all timelines in Media Pool
2. Run script (it scans and discovers: H.264, ProRes 422 HQ, DNxHD)
3. Configure rules:
   - **Rule 1**: Codec = "H.264" → "H264_to_LogC.cube" → Node 1
   - **Rule 2**: Codec = "ProRes 422 HQ" → "ProRes_to_LogC.cube" → Node 1
   - **Rule 3**: Codec = "DNxHD" → "DNxHD_to_LogC.cube" → Node 1
4. Preview to verify
5. Apply

**Result**: Each clip gets the appropriate conversion LUT based on its codec.

### Example 2: Apply LUTs by Resolution

**Scenario**: Apply different creative LUTs for 4K and HD footage.

**Steps**:
1. Select timelines
2. Run script (discovers: 3840x2160, 1920x1080)
3. Configure rules:
   - **Rule 1**: Resolution = "3840x2160" → "Creative_4K.cube" → Node 2
   - **Rule 2**: Resolution = "1920x1080" → "Creative_HD.cube" → Node 2
4. Apply

### Example 3: Apply LUTs to Multiple ProRes Variants

**Scenario**: Apply the same LUT to multiple ProRes footage variants.

**Steps**:
1. Select timelines
2. Run script (discovers: ProRes 422, ProRes 422 HQ, ProRes 4444)
3. Configure separate rules for each variant:
   - **Rule 1**: Codec = "ProRes 422" → "ProRes_Correction.cube" → Node 1
   - **Rule 2**: Codec = "ProRes 422 HQ" → "ProRes_Correction.cube" → Node 1
   - **Rule 3**: Codec = "ProRes 4444" → "ProRes_Correction.cube" → Node 1
4. Apply

**Result**: Each ProRes variant gets the same LUT applied via its specific matching rule.

### Example 4: Apply LUTs by Clip Color

**Scenario**: Apply different looks based on clip color markers set by the editor.

**Steps**:
1. Select timelines
2. Run script (discovers: Orange, Blue, Teal)
3. Configure rules:
   - **Rule 1**: Clip Color = "Orange" → "Warm_Look.cube" → Node 2
   - **Rule 2**: Clip Color = "Blue" → "Cool_Look.cube" → Node 2
   - **Rule 3**: Clip Color = "Teal" → "Teal_Look.cube" → Node 2
4. Apply

### Example 5: Multiple Nodes with Different Rules

**Scenario**: Apply conversion LUT on node 1, creative LUT on node 2 based on different properties.

**Steps**:
1. Select timelines
2. Configure rules:
   - **Rule 1**: Codec = "ProRes 422 HQ" → "ProRes_to_LogC.cube" → **Node 1**
   - **Rule 2**: Frame Rate = "23.976" → "Cinematic_Look.cube" → **Node 2**
   - **Rule 3**: Resolution = "3840x2160" → "4K_Sharpening.cube" → **Node 3**
3. Apply

### Example 6: Remove LUTs from Specific Clips

**Scenario**: Remove LUTs from all clips marked with a specific clip color, while leaving others unchanged.

**Steps**:
1. Select timelines
2. Run script (discovers clip colors including: Orange, Blue, Teal)
3. Configure rule to remove LUTs:
   - **Rule 1**: Clip Color = "Orange" → "(None - Remove LUT)" → Node 1
4. Preview to verify which clips will have LUTs removed
5. Apply

**Result**: All clips with Orange clip color have their LUT removed from node 1, while other clips remain unchanged.

**Use Case**: This is useful when you want to:
- Remove temporary LUTs applied during dailies review
- Clear LUTs from specific camera angles or takes
- Reset color grading on clips that need rework

## How Rule Matching Works

- Rules are evaluated **in order** from Rule 1 to Rule 10
- **First matching rule wins** - if a clip matches Rule 1, Rules 2-10 are not checked
- Only **enabled rules** (checkbox checked) are evaluated
- If a clip matches no rules, it is left unchanged

## Timeline Selection Behavior

- The script scans **only selected timelines** from the Media Pool to discover property values
- Dropdowns are populated with values found in the selected timelines only
- The script then processes those same selected timelines and applies LUTs

This ensures you see exactly what properties are available in the timelines you're about to process.

## Node Targeting

- **Node 1** = First color node (default)
- **Node 2** = Second color node
- etc.

**Note**: Nodes are 1-based in Resolve API (v16.2.0+)

If the specified node doesn't exist on a clip, the LUT application will fail for that clip (counted as error).

## LUT File Locations

The script scans these standard Resolve LUT folders:

**macOS:**
- `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
- `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/User/LUT/`

**Windows:**
- `C:\ProgramData\Blackmagic Design\DaVinci Resolve\LUT\`
- `%APPDATA%\Blackmagic Design\DaVinci Resolve\LUT\`

**Linux:**
- `/opt/resolve/LUT/`
- `~/.local/share/DaVinciResolve/LUT/`

Supported formats: `.cube`, `.3dl`, `.ilut`, `.dat`

## Console Mode (Resolve Free)

If UIManager is not available (Resolve Free or Studio not running), the script runs in console mode:
- Shows discovered properties
- Shows available LUTs
- Provides information only (no rule configuration)

To use with Resolve Free, edit the script and add predefined codec-to-LUT mappings in the `console_mode()` function.

## Troubleshooting

### "No items selected in Media Pool"
- Make sure you've selected items in the **Media Pool** (not Timeline)
- Items must be selected before running the script

### "Non-timeline item(s) selected"
- You selected regular clips instead of timelines
- Select timeline items (they appear as stacked film strips in Media Pool)

### "No clip properties discovered"
- Your timelines might be empty
- Make sure timelines contain clips with video tracks

### "No LUTs found"
- LUTs not in standard Resolve folders
- Add .cube, .3dl, .ilut, or .dat files to one of the LUT folders listed above
- Or use "Browse..." option (if available) to select custom path

### "Failed to apply LUT to clip"
Possible reasons:
- Specified node doesn't exist on that clip
- LUT file path invalid or moved
- Clip has no color grading nodes

### LUTs applied but no visible change
- Check you're viewing the correct timeline
- Check the specified node number is correct
- Verify LUT is actually applied (check node in Color page)

## Technical Details

### Property Discovery

The script scans selected timelines by:
1. Iterating through each selected timeline
2. Iterating through each video track with `GetItemListInTrack("video", track_idx)`
3. Extracting properties from each clip's MediaPoolItem
4. Building sets of unique values for each property type

### LUT Application and Removal

For each matching clip:
1. Get the clip's node graph: `item.GetNodeGraph(1)` (layer 1 = primary)
2. Apply or remove LUT:
   - **Apply LUT**: `graph.SetLUT(node_index, lut_path)` with file path
   - **Remove LUT**: `graph.SetLUT(node_index, "")` with empty string
3. Node indices are **1-based** (1 = first node)

**LUT Removal**: When "(None - Remove LUT)" is selected, the script calls `graph.SetLUT(node_index, "")` with an empty string, which clears the LUT from the specified node without affecting other node settings (such as color wheels, curves, or qualifiers).

### Property Matching

All property matching uses **exact match** comparison:
- String equality comparison
- Case-sensitive
- "ProRes 422" != "ProRes 422 HQ"
- Properties must match exactly as discovered from the timeline

## File Structure

```
add_luts_by_rules/
├── add_luts_by_rules.py    # Complete standalone script (no dependencies)
└── README.md              # This file
```

The script is completely self-contained with no external dependencies beyond DaVinci Resolve's API.

## Version History

### v1.0 (2025)
- Initial release
- Support for Codec, Resolution, Frame Rate, Clip Color matching
- Automatic property discovery
- Dropdown-only interface
- Preview functionality
- Multi-timeline support
- Console fallback for Free version

## See Also

- [DaVinci Resolve Scripting API Documentation](../API%20Docs/)
- [Batch Edit Script](../batch_edit/) - Component-based clip renaming
- [Find and Replace Scripts](../Find_and_Replace/) - Timeline search and replace

## Support

For issues or questions:
- Check the main repository README
- Review API documentation in `API Docs/` folder
- Ensure environment variables are set correctly (see main README)
