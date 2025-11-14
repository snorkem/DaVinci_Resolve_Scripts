# DaVinci Resolve Python Scripts

Python scripts for automating DaVinci Resolve video editing workflows using the DaVinci Resolve Scripting API.

---

## Quick Start

### Option 1: Use Scripts from Resolve's Menu (Easiest!)

**No environment setup required!** Scripts work directly from Resolve's menu.

1. **Copy scripts to Resolve's Scripts folder:**

   **Mac:**
   ```bash
   mkdir -p ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
   cp -r /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts/Find_and_Replace/*.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
   cp -r /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts/batch_edit/*.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
   cp -r /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts/add_luts_by_rules/*.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
   cp -r /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts/export_stills_from_timeline_markers/*.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
   ```

   **Windows:**
   ```cmd
   mkdir "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"
   copy Find_and_Replace\*.py "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
   copy batch_edit\*.py "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
   copy add_luts_by_rules\*.py "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
   copy export_stills_from_timeline_markers\*.py "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\"
   ```

   **Linux:**
   ```bash
   mkdir -p ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
   cp Find_and_Replace/*.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
   cp batch_edit/*.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
   cp add_luts_by_rules/*.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
   cp export_stills_from_timeline_markers/*.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/
   ```

2. **Restart DaVinci Resolve** (if it was running)

3. **Access scripts:**
   - Open DaVinci Resolve
   - Go to **Workspace → Scripts → Edit**
   - Click a script name to run it

That's it! Scripts will work without any environment configuration.

### Option 2: Run Scripts from Terminal (For Development)

If you want to run scripts from the command line for development:

1. **Configure environment variables** (one-time setup):
   ```bash
   ./setup_macos_env.sh
   ```
   Then **restart your terminal** (close and reopen).

2. **Verify setup:**
   ```bash
   python3 verify_setup.py
   ```

3. **Run scripts:**
   ```bash
   cd Find_and_Replace
   python3 show_timeline_name.py
   ```

See [`MACOS_SETUP_GUIDE.md`](MACOS_SETUP_GUIDE.md) for detailed instructions and troubleshooting.

**Windows** (System Environment Variables):
```cmd
RESOLVE_SCRIPT_API=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\
```

**Linux** (`~/.bashrc`):
```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

Then reload: `source ~/.bashrc`

### 3. Install Required Python Modules

**Important:** DaVinci Resolve uses Python 3.10. Install packages using:

```bash
python3.10 -m pip install timecode
```

This ensures packages are installed to the correct Python version that Resolve uses.

### 4. Test Your Setup

**From Resolve's menu** (no environment setup needed):
- Open DaVinci Resolve
- Open a project with a timeline
- Go to **Workspace → Scripts → Edit**
- Try running any of the available scripts (see "Available Scripts" section below)

**From terminal** (requires environment setup):
```bash
python3 verify_setup.py
```

---

## Repository Structure

- **`add_luts_by_rules/`** - Automated LUT application based on clip property rules
- **`batch_edit/`** - Component-based clip renaming tool
- **`export_stills_from_timeline_markers/`** - Export still images from timeline markers
- **`Find_and_Replace/`** - Find and replace clip and timeline names in Media Pool
- **`setup_macos_env.sh`** - Automated macOS environment setup script
- **`verify_setup.py`** - Setup verification script

---

## Available Scripts

### Add LUTs by Rules
- **`add_luts_by_rules/add_luts_by_rules.py`** - Automatically apply or remove LUTs from timeline clips based on property matching rules (codec, resolution, frame rate, clip color)
- Features dropdown-only interface, exact property matching, and preview before applying changes
- See [`add_luts_by_rules/README.md`](add_luts_by_rules/README.md) for detailed documentation

### Batch Edit
- **`batch_edit/batch_edit.py`** - Component-based clip renaming tool for clips and timelines in the Media Pool
- See [`batch_edit/README.md`](batch_edit/README.md) for detailed documentation

### Export Stills from Timeline Markers
- **`export_stills_from_timeline_markers/export_stills_from_timeline_markers.py`** - Export still images at timeline marker positions
- Supports filtering by marker color or exporting all markers
- See [`export_stills_from_timeline_markers/README.md`](export_stills_from_timeline_markers/README.md) for detailed documentation

### Find and Replace
- **`Find_and_Replace/find_and_replace_selected.py`** - Find and replace text in timeline clips, markers, and metadata
- See [`Find_and_Replace/README.md`](Find_and_Replace/README.md) for detailed documentation

**All scripts work in both terminal and Resolve menu contexts!**

---

## Requirements

- **DaVinci Resolve 16.2+** (Free or Studio)
- **Python 3.10** (64-bit) - DaVinci Resolve uses Python 3.10
- **timecode module** (`python3.10 -m pip install timecode`)

**Note:** UI dialogs only work in DaVinci Resolve Studio. Free version scripts fall back to console output.

---

## Documentation

Complete API documentation is available in the `API Docs/` folder:

1. **DaVinci_Resolve_API_Complete.md** - Full API reference
2. **Quick_Start_Guide.md** - Getting started with examples
3. **Render_Settings_Reference.md** - Render configuration guide
4. **Timeline_Operations_Reference.md** - Timeline editing reference

---

## Running Scripts from DaVinci Resolve

Scripts can be accessed from Resolve's Workspace menu once installed to the Scripts folder.

**Installation:** See "Option 1: Use Scripts from Resolve's Menu" above for complete installation commands.

**Scripts folder locations:**
- **Mac:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Edit/`
- **Windows:** `%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`
- **Linux:** `$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Edit/`

**Access:** **Workspace → Scripts → Edit → [Script Name]**

---

## License

Scripts in this repository are provided as-is for use with DaVinci Resolve.

---

## Troubleshooting

### "Could not import DaVinciResolveScript module"

**From Resolve's menu:**
- This shouldn't happen! Scripts handle module paths automatically
- Make sure you copied all scripts to the Scripts folder (see installation instructions)

**From terminal:**
- Environment variables are not set correctly
- Run `python3 verify_setup.py` for detailed diagnostics
- Run `./setup_macos_env.sh` to configure environment

### "Could not connect to DaVinci Resolve"
- Make sure DaVinci Resolve is running
- Only one script can connect at a time
- Try closing and reopening Resolve

### Scripts work in Studio but not Free version
- UI dialogs (UIManager) are not available in the Free version
- Scripts should fall back to console output automatically
- This is expected behavior, not an error

### Scripts work from terminal but not from Resolve menu
- Make sure you copied the scripts to Resolve's Scripts folder (see Option 1 above)
- Check that all required dependencies are installed (`python3.10 -m pip install timecode`)
- Restart DaVinci Resolve after copying scripts

For more help:
- **From terminal:** Run `python3 verify_setup.py`
- Check the specific script's README.md for additional requirements
