# DaVinci Resolve Python Scripts

Python scripts for automating DaVinci Resolve video editing workflows using the DaVinci Resolve Scripting API.

---

## Quick Start

### Option 1: Use Scripts from Resolve's Menu (Easiest!)

**No environment setup required!** Scripts work directly from Resolve's menu.

1. **Install scripts to Resolve:**
   ```bash
   cd /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts
   ./install_scripts.sh
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

```bash
pip install timecode
```

### 4. Test Your Setup

**From Resolve's menu** (no environment setup needed):
- Open DaVinci Resolve
- Go to **Workspace → Scripts → Edit → hello_world_dialog** for a simple test
- Run **check_studio_version** to see if you have Studio or Free version
- Open a project and timeline, then try **show_timeline_name** from the same menu

**From terminal** (requires environment setup):
```bash
cd Find_and_Replace
python3 test_resolve_context.py
python3 show_timeline_name.py
```

---

## Repository Structure

- **`API Docs/`** - Complete DaVinci Resolve API reference documentation
- **`Find_and_Replace/`** - Find and replace tools for timeline editing
- **`verify_setup.py`** - Setup verification script
- **`CLAUDE.md`** - Developer guide for working with this repository

---

## Available Scripts

### Find and Replace

Located in `Find_and_Replace/` folder:

- **`resolve_utils.py`** - Common utility module (imported by other scripts)
- **`hello_world_dialog.py`** - Simple "Hello, World!" dialog test
- **`check_studio_version.py`** - Detects whether you have Studio or Free version
- **`show_timeline_name.py`** - Displays the current timeline name in a dialog (self-contained, no dependencies)
- **`test_resolve_context.py`** - Diagnostic script showing execution context
- **`test_package_import.py`** - Tests if pip-installed packages are accessible from Resolve

**All scripts work in both terminal and Resolve menu contexts!**

See [`PACKAGE_INSTALL_TEST.md`](PACKAGE_INSTALL_TEST.md) for testing package installation.

More scripts coming soon!

---

## Requirements

- **DaVinci Resolve 16.2+** (Free or Studio)
- **Python 3.6+** (64-bit)
- **timecode module** (`pip install timecode`)

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

To access scripts from Resolve's Workspace menu:

1. Copy scripts to your Resolve Scripts folder:
   - **Mac:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Edit/`
   - **Windows:** `%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`
   - **Linux:** `$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Edit/`

2. Restart DaVinci Resolve

3. Access from: **Workspace → Scripts → Edit → [Script Name]**

---

## Contributing

See `CLAUDE.md` for development guidelines and architecture details.

**Important:** Always update `CLAUDE.md` when making significant changes or adding new features.

---

## License

Scripts in this repository are provided as-is for use with DaVinci Resolve.

---

## Troubleshooting

### "Could not import DaVinciResolveScript module"

**From Resolve's menu:**
- This shouldn't happen! Scripts use `resolve_utils.py` which handles module paths automatically
- Try running `test_resolve_context` from Resolve's menu to diagnose
- Make sure you copied `resolve_utils.py` along with other scripts

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
- Make sure you installed scripts using `./install_scripts.sh`
- Make sure `resolve_utils.py` is in the same folder as other scripts
- Try running `test_resolve_context` from both contexts to compare

For more help:
- **From terminal:** Run `python3 verify_setup.py`
- **From Resolve:** Run **Workspace → Scripts → Edit → test_resolve_context**
