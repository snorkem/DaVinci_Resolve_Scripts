#!/usr/bin/env python3
"""
DaVinci Resolve Setup Verification Script
Checks that all requirements are met for running DaVinci Resolve Python scripts.
"""
import sys
import os
import platform
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_status(check_name, passed, message=""):
    """Print a check result with status."""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {check_name}")
    if message:
        print(f"      {message}")


def check_operating_system():
    """Check and display operating system information."""
    print_header("Operating System")
    os_name = platform.system()
    os_version = platform.version()
    print(f"OS: {os_name}")
    print(f"Version: {os_version}")
    print(f"Python: {sys.version}")
    return os_name


def check_resolve_installation(os_name):
    """Check if DaVinci Resolve is installed."""
    print_header("DaVinci Resolve Installation")

    if os_name == "Darwin":  # macOS
        resolve_path = Path("/Applications/DaVinci Resolve/DaVinci Resolve.app")
        script_api_path = Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
        script_lib_path = Path("/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
    elif os_name == "Windows":
        resolve_path = Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / "Blackmagic Design/DaVinci Resolve"
        script_api_path = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting"
        script_lib_path = Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / "Blackmagic Design/DaVinci Resolve/fusionscript.dll"
    else:  # Linux
        resolve_path = Path("/opt/resolve")
        script_api_path = Path("/opt/resolve/Developer/Scripting")
        script_lib_path = Path("/opt/resolve/libs/Fusion/fusionscript.so")

    # Check Resolve installation
    resolve_installed = resolve_path.exists()
    print_status("DaVinci Resolve Installation", resolve_installed,
                 str(resolve_path) if resolve_installed else "Not found at expected location")

    # Check Script API path
    api_exists = script_api_path.exists()
    print_status("Scripting API Path", api_exists, str(script_api_path))

    # Check Script Library
    lib_exists = script_lib_path.exists()
    print_status("Fusion Script Library", lib_exists, str(script_lib_path))

    # Check for Python module
    if api_exists:
        module_path = script_api_path / "Modules" / "DaVinciResolveScript.py"
        module_exists = module_path.exists()
        print_status("DaVinciResolveScript Module", module_exists, str(module_path))
    else:
        module_exists = False
        print_status("DaVinciResolveScript Module", False, "API path not found")

    return {
        'resolve_path': resolve_path,
        'script_api_path': script_api_path,
        'script_lib_path': script_lib_path,
        'all_present': resolve_installed and api_exists and lib_exists and module_exists
    }


def check_environment_variables(os_name, paths):
    """Check if environment variables are set correctly."""
    print_header("Environment Variables")

    if os_name == "Darwin":  # macOS
        expected_api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
        expected_lib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif os_name == "Windows":
        expected_api = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'),
                                   "Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting")
        expected_lib = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                                   "Blackmagic Design\\DaVinci Resolve\\fusionscript.dll")
    else:  # Linux
        expected_api = "/opt/resolve/Developer/Scripting"
        expected_lib = "/opt/resolve/libs/Fusion/fusionscript.so"

    # Check RESOLVE_SCRIPT_API
    script_api = os.environ.get('RESOLVE_SCRIPT_API')
    api_set = script_api is not None
    print_status("RESOLVE_SCRIPT_API", api_set,
                 script_api if api_set else "Not set")

    # Check RESOLVE_SCRIPT_LIB
    script_lib = os.environ.get('RESOLVE_SCRIPT_LIB')
    lib_set = script_lib is not None
    print_status("RESOLVE_SCRIPT_LIB", lib_set,
                 script_lib if lib_set else "Not set")

    # Check PYTHONPATH
    pythonpath = os.environ.get('PYTHONPATH', '')
    modules_path = os.path.join(expected_api, "Modules")
    pythonpath_set = modules_path in pythonpath
    print_status("PYTHONPATH includes Modules/", pythonpath_set,
                 "Contains Resolve modules path" if pythonpath_set else "Missing Resolve modules path")

    all_set = api_set and lib_set and pythonpath_set

    if not all_set:
        print("\n" + "-" * 70)
        print("To fix, add these to your shell profile:")
        if os_name == "Darwin":
            print("\n# For ~/.zshrc or ~/.bash_profile:")
        elif os_name == "Windows":
            print("\n# For System Environment Variables:")
        else:
            print("\n# For ~/.bashrc:")

        print(f'export RESOLVE_SCRIPT_API="{expected_api}"')
        print(f'export RESOLVE_SCRIPT_LIB="{expected_lib}"')
        print(f'export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"')

        if os_name == "Darwin":
            print("\nThen run: source ~/.zshrc  (or source ~/.bash_profile)")
        elif os_name == "Windows":
            print("\nThen restart your terminal/IDE")
        else:
            print("\nThen run: source ~/.bashrc")

    return all_set


def check_python_import():
    """Check if Python can import DaVinciResolveScript."""
    print_header("Python Module Import")

    try:
        import DaVinciResolveScript as dvr_script
        print_status("Import DaVinciResolveScript", True, "Module imported successfully")
        return True, dvr_script
    except ImportError as e:
        print_status("Import DaVinciResolveScript", False, str(e))
        print("\n" + "-" * 70)
        print("Python cannot find the DaVinciResolveScript module.")
        print("Make sure environment variables are set (see above) and restart your terminal.")
        return False, None
    except Exception as e:
        print_status("Import DaVinciResolveScript", False, f"Unexpected error: {e}")
        return False, None


def check_resolve_connection(dvr_script):
    """Check if we can connect to a running DaVinci Resolve instance."""
    print_header("DaVinci Resolve Connection")

    if not dvr_script:
        print_status("Connect to Resolve", False, "Module import failed - skipping connection test")
        return False

    try:
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            print_status("Connect to Resolve", True, "Successfully connected to running instance")

            # Get version info
            try:
                version = resolve.GetVersionString()
                print(f"      DaVinci Resolve Version: {version}")
            except:
                pass

            # Check for open project
            try:
                pm = resolve.GetProjectManager()
                project = pm.GetCurrentProject()
                if project:
                    project_name = project.GetName()
                    print_status("Current Project", True, f'"{project_name}"')

                    # Check for timeline
                    timeline = project.GetCurrentTimeline()
                    if timeline:
                        timeline_name = timeline.GetName()
                        print_status("Current Timeline", True, f'"{timeline_name}"')
                    else:
                        print_status("Current Timeline", False, "No timeline is active")
                else:
                    print_status("Current Project", False, "No project is open")
            except Exception as e:
                print_status("Project/Timeline Check", False, str(e))

            return True
        else:
            print_status("Connect to Resolve", False, "DaVinci Resolve is not running")
            print("\n" + "-" * 70)
            print("Please start DaVinci Resolve and try again.")
            return False
    except Exception as e:
        print_status("Connect to Resolve", False, str(e))
        return False


def check_python_path():
    """Display Python's module search paths."""
    print_header("Python Module Search Paths")
    print("Python will search these paths for modules:")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")


def print_summary(checks):
    """Print overall summary."""
    print_header("Summary")

    all_passed = all(checks.values())

    if all_passed:
        print("\n✓ All checks passed! Your system is ready to run DaVinci Resolve scripts.")
        print("\nYou can now run scripts like:")
        print("  python3 show_timeline_name.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nFailed checks:")
        for check, passed in checks.items():
            if not passed:
                print(f"  - {check}")

    print()


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  DaVinci Resolve Python Scripting - Setup Verification")
    print("=" * 70)

    checks = {}

    # 1. Check OS
    os_name = check_operating_system()

    # 2. Check Resolve installation
    paths = check_resolve_installation(os_name)
    checks['Resolve Installation'] = paths['all_present']

    # 3. Check environment variables
    env_vars_set = check_environment_variables(os_name, paths)
    checks['Environment Variables'] = env_vars_set

    # 4. Show Python paths
    check_python_path()

    # 5. Try importing the module
    can_import, dvr_script = check_python_import()
    checks['Module Import'] = can_import

    # 6. Try connecting to Resolve
    can_connect = check_resolve_connection(dvr_script)
    checks['Resolve Connection'] = can_connect

    # 7. Print summary
    print_summary(checks)

    return all(checks.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
