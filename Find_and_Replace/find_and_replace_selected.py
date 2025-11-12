#!/usr/bin/env python3.10
"""
Timeline Metadata Find and Replace
Allows users to find and replace text in clip properties and metadata.

This script:
1. Gets selected clips from the Media Pool
2. Shows a dialog with all available editable properties:
   - Name (via SetName)
   - Clip Color (via SetClipProperty)
   - Metadata properties (via SetMetadata)
3. Allows find/replace operations on the selected property across all selected clips
"""
from __future__ import annotations
from typing import Any
import sys
import os
import platform
import traceback


def add_resolve_module_path() -> bool:
    """Add DaVinci Resolve's module path to sys.path."""
    os_name = platform.system()

    if os_name == "Darwin":  # macOS
        module_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    elif os_name == "Windows":
        programdata = os.environ.get('PROGRAMDATA', 'C:/ProgramData')
        module_path = os.path.join(programdata,
                                   "Blackmagic Design",
                                   "DaVinci Resolve",
                                   "Support",
                                   "Developer",
                                   "Scripting",
                                   "Modules")
    elif os_name == "Linux":
        module_path = "/opt/resolve/Developer/Scripting/Modules/"
    else:
        return False

    if module_path not in sys.path:
        sys.path.insert(0, module_path)
    return True


def get_resolve() -> Any | None:
    """Get the DaVinci Resolve scripting API object."""
    add_resolve_module_path()

    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("ERROR: Could not connect to DaVinci Resolve.")
            return None
        return resolve
    except Exception as e:
        print(f"ERROR: {e}")
        return None


class TimelineMetadataEditor:
    """Handles timeline metadata find and replace operations."""

    def __init__(self, resolve: Any):
        """
        Initialize the metadata editor.

        Args:
            resolve: DaVinci Resolve application object
        """
        self.resolve = resolve
        self.project = None
        self.media_pool = None
        self.selected_items: list[Any] = []
        self.metadata_properties: list[str] = []
        self.editable_properties: list[str] = []

    def initialize(self) -> bool:
        """
        Initialize all necessary Resolve objects.

        Returns:
            True if successful, False otherwise
        """
        # Get project
        try:
            pm = self.resolve.GetProjectManager()
            if not pm:
                print("ERROR: Could not access Project Manager")
                return False

            self.project = pm.GetCurrentProject()
            if not self.project:
                print("ERROR: No project is currently open")
                return False
        except Exception as e:
            print(f"ERROR: Failed to get project: {e}")
            return False

        # Get media pool
        try:
            self.media_pool = self.project.GetMediaPool()
            if not self.media_pool:
                print("ERROR: Could not access Media Pool")
                return False
        except Exception as e:
            print(f"ERROR: Failed to get Media Pool: {e}")
            return False

        # Get selected items from Media Pool
        try:
            # Try to get selected clips first
            self.selected_items = self.media_pool.GetSelectedClips()

            if not self.selected_items:
                print("WARNING: No clips selected in Media Pool")
                print("         Please select clips in the Media Pool and try again")
                return False

            print(f"Found {len(self.selected_items)} selected item(s)")

        except Exception as e:
            print(f"ERROR: Failed to get selected clips: {e}")
            return False

        # Get metadata properties from first item
        try:
            first_item = self.selected_items[0]
            metadata = first_item.GetMetadata()
            if not metadata:
                print("WARNING: No metadata available")
                self.metadata_properties = []
            else:
                self.metadata_properties = list(metadata.keys())

            # Add special editable properties: Name and Clip Color
            # "Name" uses SetName(), "Clip Color" uses SetClipProperty()
            self.editable_properties = ["Name", "Clip Color"] + self.metadata_properties

        except Exception as e:
            print(f"ERROR: Failed to get metadata: {e}")
            return False

        return True

    def _process_item_property(self, item: Any, property_name: str, find_text: str, replace_text: str) -> tuple[bool, str]:
        """
        Process find/replace for a single item property.

        Args:
            item: Media pool item to process
            property_name: Property to modify
            find_text: Text to find
            replace_text: Text to replace with

        Returns:
            Tuple of (success: bool, status: 'modified'|'skipped'|'error')
        """
        try:
            # Get current value based on property type
            if property_name == "Name":
                current_value = item.GetName()
            elif property_name == "Clip Color":
                current_value = item.GetClipProperty(property_name)
                current_value = str(current_value) if current_value else ""
            else:  # Metadata property
                metadata = item.GetMetadata()
                if metadata is None:
                    return False, 'skipped'
                current_value = metadata.get(property_name, "")

            # Check if find_text exists
            if find_text not in current_value:
                return False, 'skipped'

            # Perform replacement
            new_value = current_value.replace(find_text, replace_text)

            # Set new value based on property type
            if property_name == "Name":
                result = item.SetName(new_value)
            elif property_name == "Clip Color":
                result = item.SetClipProperty(property_name, new_value)
            else:  # Metadata property
                result = item.SetMetadata(property_name, new_value)

            return result, 'modified' if result else 'error'

        except Exception as e:
            print(f"ERROR processing item: {e}")
            return False, 'error'

    def find_and_replace(self, property_name: str, find_text: str, replace_text: str) -> tuple[bool, str]:
        """
        Find and replace text in a metadata property for all selected items.

        Args:
            property_name: Name of the metadata property to modify (or "Name" for item name)
            find_text: Text to find
            replace_text: Text to replace with

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.selected_items:
                return False, "No items selected"

            if not property_name or property_name not in self.editable_properties:
                return False, f"Invalid property: {property_name}"

            modified_count = 0
            skipped_count = 0
            error_count = 0

            # Process each selected item
            for item in self.selected_items:
                success, status = self._process_item_property(item, property_name, find_text, replace_text)

                if status == 'modified':
                    modified_count += 1
                elif status == 'skipped':
                    skipped_count += 1
                else:  # 'error'
                    error_count += 1

            # Build result message
            total = len(self.selected_items)
            message_parts = [
                f"{modified_count} item(s) modified" if modified_count > 0 else None,
                f"{skipped_count} skipped (text not found)" if skipped_count > 0 else None,
                f"{error_count} error(s)" if error_count > 0 else None,
            ]
            message = f"{', '.join(filter(None, message_parts))} out of {total} total"

            success = modified_count > 0
            return success, message

        except Exception as e:
            return False, f"Error: {e}"


class FindReplaceDialog:
    """Manages the find/replace dialog UI."""

    def __init__(self, resolve: Any, editor: TimelineMetadataEditor):
        """
        Initialize the dialog.

        Args:
            resolve: DaVinci Resolve application object
            editor: TimelineMetadataEditor instance
        """
        self.resolve = resolve
        self.editor = editor
        self.fusion = None
        self.ui = None
        self.disp = None
        self.window = None

    def create_dialog(self) -> bool:
        """
        Create and show the find/replace dialog.

        Returns:
            True if successful, False otherwise
        """
        try:
            import DaVinciResolveScript as dvr

            # Get Fusion and UIManager
            self.fusion = self.resolve.Fusion()
            if not self.fusion:
                print("ERROR: Could not access Fusion")
                return False

            self.ui = self.fusion.UIManager
            if not self.ui:
                print("ERROR: Could not access UIManager (Studio version required)")
                return False

            # Create UIDispatcher instance
            self.disp = dvr.UIDispatcher(self.ui)

            # Get item count for display
            item_count = len(self.editor.selected_items)
            items_text = f"Processing {item_count} selected item(s) from Media Pool"

            # Create dropdown items for metadata properties
            combo_items = self.editor.editable_properties

            # Create dialog window
            self.window = self.disp.AddWindow({
                "WindowTitle": "Timeline Metadata Find & Replace",
                "ID": "FindReplaceDialog",
                "Geometry": [100, 100, 500, 300],
            }, [
                self.ui.VGroup([
                    # Item count display
                    self.ui.Label({
                        "Text": items_text,
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 14, "Bold": True}),
                    }),
                    self.ui.VGap(10),

                    # Property selector
                    self.ui.HGroup([
                        self.ui.Label({"Text": "Property:", "Weight": 0, "MinimumSize": [80, 0]}),
                        self.ui.ComboBox({
                            "ID": "PropertyCombo",
                            "Weight": 1,
                        }),
                    ]),
                    self.ui.VGap(5),

                    # Find text field
                    self.ui.HGroup([
                        self.ui.Label({"Text": "Find:", "Weight": 0, "MinimumSize": [80, 0]}),
                        self.ui.LineEdit({
                            "ID": "FindText",
                            "PlaceholderText": "Text to find...",
                            "Weight": 1,
                        }),
                    ]),
                    self.ui.VGap(5),

                    # Replace text field
                    self.ui.HGroup([
                        self.ui.Label({"Text": "Replace:", "Weight": 0, "MinimumSize": [80, 0]}),
                        self.ui.LineEdit({
                            "ID": "ReplaceText",
                            "PlaceholderText": "Replace with...",
                            "Weight": 1,
                        }),
                    ]),
                    self.ui.VGap(10),

                    # Status message
                    self.ui.Label({
                        "ID": "StatusLabel",
                        "Text": "Select a property and enter find/replace text",
                        "Weight": 0,
                        "StyleSheet": "QLabel { color: #666; }",
                    }),
                    self.ui.VGap(10),

                    # Buttons
                    self.ui.HGroup([
                        self.ui.HGap(0, 1),
                        self.ui.Button({
                            "ID": "ReplaceButton",
                            "Text": "Replace",
                            "MinimumSize": [100, 30],
                        }),
                        self.ui.Button({
                            "ID": "CloseButton",
                            "Text": "Close",
                            "MinimumSize": [100, 30],
                        }),
                    ]),
                ]),
            ])

            # Get window items
            itm = self.window.GetItems()

            # Populate combo box
            itm["PropertyCombo"].AddItems(combo_items)
            if combo_items:
                itm["PropertyCombo"].SetCurrentText(combo_items[0])

            # Set up event handlers
            self.window.On.FindReplaceDialog.Close = lambda ev: self.on_close(ev)
            self.window.On.CloseButton.Clicked = lambda ev: self.on_close(ev)
            self.window.On.ReplaceButton.Clicked = lambda ev: self.on_replace(ev)

            # Show window
            self.window.Show()
            self.disp.RunLoop()
            self.window.Hide()

            return True

        except Exception as e:
            print(f"ERROR: Failed to create dialog: {e}")
            traceback.print_exc()
            return False

    def on_replace(self, ev: Any) -> None:
        """Handle Replace button click."""
        try:
            itm = self.window.GetItems()

            property_name = itm["PropertyCombo"].CurrentText
            find_text = itm["FindText"].Text
            replace_text = itm["ReplaceText"].Text

            # Validate inputs
            if not find_text:
                itm["StatusLabel"].Text = "ERROR: Please enter text to find"
                itm["StatusLabel"].StyleSheet = "QLabel { color: red; }"
                return

            # Perform find and replace
            success, message = self.editor.find_and_replace(property_name, find_text, replace_text)

            # Update status
            itm["StatusLabel"].Text = message
            itm["StatusLabel"].StyleSheet = f"QLabel {{ color: {'green' if success else 'red'}; }}"

        except Exception as e:
            print(f"ERROR in on_replace: {e}")
            traceback.print_exc()

    def on_close(self, ev: Any) -> None:
        """Handle window close."""
        self.disp.ExitLoop()


def main() -> bool:
    """Main function."""
    print("\n" + "=" * 70)
    print("  Timeline Metadata Find & Replace")
    print("=" * 70)

    resolve = get_resolve()
    if not resolve:
        return False

    # Create editor
    editor = TimelineMetadataEditor(resolve)

    print("\nInitializing...")
    if not editor.initialize():
        print("ERROR: Failed to initialize")
        return False

    print(f"✓ Found {len(editor.selected_items)} selected item(s)")
    print(f"✓ Found {len(editor.editable_properties)} editable properties (including Name and Clip Color)")

    # Create and show dialog
    print("\nOpening dialog...")
    dialog = FindReplaceDialog(resolve, editor)
    dialog.create_dialog()

    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    success: bool = main()
    sys.exit(0 if success else 1)
