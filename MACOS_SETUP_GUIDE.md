# macOS Environment Setup Guide

Complete guide for setting up DaVinci Resolve Python scripting environment on macOS.

---

## Automated Setup (Recommended)

Run the automated setup script:

```bash
cd /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts
./setup_macos_env.sh
```

This script will:
- ✓ Detect your shell (zsh or bash)
- ✓ Verify DaVinci Resolve is installed
- ✓ Add environment variables to the correct config file
- ✓ Create a backup of your config file
- ✓ Verify the setup worked

**After running the script:**
1. **Close your terminal completely**
2. **Open a new terminal window**
3. **Verify the setup:** `python3 verify_setup.py`

---

## Manual Setup

If the automated script doesn't work, follow these manual steps:

### Step 1: Determine Your Shell

```bash
echo $SHELL
```

- If it says `/bin/zsh` → you're using Zsh (modern macOS default)
- If it says `/bin/bash` → you're using Bash

### Step 2: Edit the Correct Config File

**For Zsh (most common):**

```bash
nano ~/.zshrc
```

**For Bash:**

```bash
nano ~/.bash_profile
```

(Use `nano ~/.bashrc` if `.bash_profile` doesn't exist)

### Step 3: Add These Lines

Add the following lines at the **end** of the file:

```bash
# DaVinci Resolve Scripting Environment Variables
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

**In nano editor:**
- Type or paste the lines above
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### Step 4: Apply the Changes

**Option 1 (Recommended):** Restart Terminal
- Close the terminal window completely
- Open a new terminal window

**Option 2:** Reload the config file

For Zsh:
```bash
source ~/.zshrc
```

For Bash:
```bash
source ~/.bash_profile
```

### Step 5: Verify It Worked

```bash
# Check if variables are set
echo $RESOLVE_SCRIPT_API

# Should print:
# /Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting
```

If you see the path above, it worked! If not, see troubleshooting below.

### Step 6: Run Full Verification

```bash
cd /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts
python3 verify_setup.py
```

---

## Troubleshooting

### Problem: Variables Not Set After Reloading

**Cause:** Terminal might not be reading your config file.

**Solution:**

1. Check which config file your shell actually uses:
   ```bash
   echo $SHELL
   ls -la ~/ | grep -E 'zshrc|bash_profile|bashrc'
   ```

2. Make sure you edited the right file for your shell

3. Try restarting your terminal completely instead of using `source`

4. Check for syntax errors in your config file:
   ```bash
   # For Zsh
   zsh -n ~/.zshrc

   # For Bash
   bash -n ~/.bash_profile
   ```

### Problem: Still Getting Import Error

**Cause:** PYTHONPATH might not include the Modules directory.

**Solution:**

1. Check your PYTHONPATH:
   ```bash
   echo $PYTHONPATH
   ```

2. Verify the Modules directory exists:
   ```bash
   ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
   ```

3. You should see `DaVinciResolveScript.py` in that directory

4. Try setting PYTHONPATH directly in the terminal to test:
   ```bash
   export PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
   python3 -c "import DaVinciResolveScript; print('Success!')"
   ```

### Problem: Permission Denied

**Cause:** The setup script isn't executable.

**Solution:**
```bash
chmod +x setup_macos_env.sh
./setup_macos_env.sh
```

### Problem: DaVinci Resolve Not Found

**Cause:** DaVinci Resolve isn't installed in the default location.

**Solution:**

1. Find where Resolve is installed:
   ```bash
   mdfind "DaVinci Resolve.app" | grep Applications
   ```

2. Check if the Scripting API exists:
   ```bash
   ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
   ```

3. If not found, reinstall DaVinci Resolve

### Problem: Variables Set But Python Still Can't Import

**Cause:** Multiple Python installations or virtual environments.

**Solution:**

1. Check which Python you're using:
   ```bash
   which python3
   python3 --version
   ```

2. Check Python's sys.path:
   ```bash
   python3 -c "import sys; print('\n'.join(sys.path))"
   ```

3. Make sure the Modules directory appears in the list

4. Try running with full PYTHONPATH:
   ```bash
   PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/" python3 verify_setup.py
   ```

---

## Verification Checklist

Run these commands to verify everything is correct:

```bash
# 1. Check shell
echo $SHELL

# 2. Check environment variables
echo $RESOLVE_SCRIPT_API
echo $RESOLVE_SCRIPT_LIB
echo $PYTHONPATH

# 3. Check DaVinci Resolve installation
ls "/Applications/DaVinci Resolve/DaVinci Resolve.app"

# 4. Check Scripting API
ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"

# 5. Check Python can find module
python3 -c "import sys; print('/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/' in sys.path)"

# 6. Try importing
python3 -c "import DaVinciResolveScript; print('Success!')"

# 7. Run full verification
python3 verify_setup.py
```

All checks should pass ✓

---

## Alternative: Set Variables Per Session

If you don't want to modify your shell config, you can set variables for each terminal session:

```bash
# Run these commands before using the scripts
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

# Then run your script
python3 show_timeline_name.py
```

**Note:** You'll need to run these export commands in every new terminal session.

---

## For IDE Users (PyCharm, VS Code, etc.)

If you're using an IDE, you may need to restart it after setting environment variables:

1. Set up environment variables using the automated script or manual method
2. **Completely quit** your IDE (not just close the window)
3. Restart the IDE
4. The IDE should now pick up the environment variables

For VS Code specifically, you can also add to `.vscode/settings.json`:

```json
{
  "terminal.integrated.env.osx": {
    "RESOLVE_SCRIPT_API": "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting",
    "RESOLVE_SCRIPT_LIB": "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
    "PYTHONPATH": "${env:PYTHONPATH}:/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
  }
}
```

---

## Still Having Issues?

1. Run the diagnostic script for detailed information:
   ```bash
   python3 verify_setup.py
   ```

2. Check the backup of your config file if something went wrong:
   ```bash
   ls -la ~/ | grep backup
   ```

3. Restore from backup if needed:
   ```bash
   cp ~/.zshrc.backup.XXXXXXXX ~/.zshrc
   source ~/.zshrc
   ```

4. Make sure DaVinci Resolve is actually running when testing scripts

5. Try the simplest possible test:
   ```bash
   cd /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts
   export PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
   python3 -c "import DaVinciResolveScript; print('Works!')"
   ```

---

## Running Scripts from DaVinci Resolve's Menu

The environment setup above is **only needed for running scripts from the terminal**. Scripts in this repository are now designed to work from **both** contexts:

1. **Terminal execution** - Uses your shell's environment variables
2. **Resolve menu execution** - Works WITHOUT environment variables

### How It Works

Scripts in this repository use the `resolve_utils.py` module which automatically:
- Detects your operating system
- Adds the correct module path to `sys.path`
- Handles imports regardless of execution context
- Provides helpful error messages

This means **scripts will work from Resolve's Workspace menu even if you haven't set up environment variables**.

### Installing Scripts to Resolve's Menu

To make scripts accessible from **Workspace → Scripts** in DaVinci Resolve:

#### Automated Installation (Recommended)

```bash
cd /Users/Alex/Documents/Python_Projects/DaVinci_Resolve_Scripts
./install_scripts.sh
```

This will:
- Copy scripts to `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Edit/`
- Make scripts executable
- Create the directory structure if needed

#### Manual Installation

Copy scripts manually:

```bash
# Create the directory
mkdir -p ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/

# Copy scripts
cp Find_and_Replace/*.py ~/Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/Support/Fusion/Scripts/Edit/
```

#### Accessing Scripts in Resolve

1. Restart DaVinci Resolve (if it was running during installation)
2. Go to **Workspace → Scripts → Edit**
3. You should see your scripts listed there
4. Click a script name to run it

### Testing From Resolve's Menu

After installing scripts:

1. Open DaVinci Resolve
2. Open a project and timeline
3. Go to **Workspace → Scripts → Edit → test_resolve_context**
4. This will show detailed diagnostic information about the execution context
5. Then try **Workspace → Scripts → Edit → show_timeline_name**

### Key Differences: Terminal vs Resolve Menu

| Aspect | Terminal Execution | Resolve Menu Execution |
|--------|-------------------|------------------------|
| Environment Variables | Uses your shell's variables | Doesn't inherit shell variables |
| Python Interpreter | System Python (from PATH) | Resolve's Python environment |
| Module Path | Set via PYTHONPATH | Set via `sys.path.insert()` in script |
| Setup Required | Must configure shell profile | No setup required (automatic) |
| Console Output | Visible in terminal | May not be visible (use dialogs) |

### Why Scripts Now Work in Both Contexts

Scripts use two techniques to work in both contexts:

**1. Module Path Handling** - The `resolve_utils.py` module includes:

```python
def add_resolve_module_path():
    """Add DaVinci Resolve's module path to sys.path."""
    module_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    if module_path not in sys.path:
        sys.path.insert(0, module_path)
```

This is called **before** importing `DaVinciResolveScript`, ensuring the module can be found regardless of whether `PYTHONPATH` is set.

**2. __file__ Variable Handling** - The `__file__` variable is **not defined** when scripts run from Resolve's menu. Scripts handle this:

```python
try:
    # Try to get directory from __file__ (terminal execution)
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ not defined (Resolve menu execution)
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv[0] else os.getcwd()
```

This ensures scripts can find `resolve_utils.py` regardless of execution context.

### Recommendation

**For Development:**
- Set up environment variables using this guide
- Run scripts from terminal for easier debugging
- See console output and error messages

**For End Users:**
- Just install scripts to Resolve's menu
- No environment setup needed
- Scripts work immediately

Both approaches now work correctly!
