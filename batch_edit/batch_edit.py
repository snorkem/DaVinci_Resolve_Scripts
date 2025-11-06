#!/usr/bin/env python3.10
"""
Batch Edit - Component-Based Batch Renaming
Build new clip names from scratch by chaining components together.

Supported Components:
- Counter: Sequential numbers with padding
- Specified Text: Custom text strings
- Column Data: Pull from clip properties (Name, Clip Color, metadata)
"""
from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
import sys
import os
import platform


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


class Component(ABC):
    """Abstract base class for name components."""

    @abstractmethod
    def generate(self, item: Any, index: int, previous_result: str) -> str:
        """
        Generate component output.

        Args:
            item: Media pool item
            index: Index of item in selection (for counter)
            previous_result: Result from previous component

        Returns:
            String output for this component
        """
        pass


class CounterComponent(Component):
    """Sequential number component."""

    def __init__(self, start: int = 1, padding: int = 3, increment: int = 1):
        self.start = start
        self.padding = padding
        self.increment = increment

    def generate(self, item: Any, index: int, previous_result: str) -> str:
        """Generate counter value."""
        value = self.start + (index * self.increment)
        return str(value).zfill(self.padding)


class SpecifiedTextComponent(Component):
    """Custom text component."""

    def __init__(self, text: str = ""):
        self.text = text

    def generate(self, item: Any, index: int, previous_result: str) -> str:
        """Return custom text."""
        return self.text


class ColumnDataComponent(Component):

    """Clip property data component."""

    def __init__(self, column: str = "Name"):
        self.column = column

    def generate(self, item: Any, index: int, previous_result: str) -> str:
        """Get data from clip property."""
        try:
            if self.column == "Name":
                return item.GetName()
            elif self.column == "Clip Color":
                color = item.GetClipProperty("Clip Color")
                return color if color else ""
            else:
                # Try metadata
                metadata = item.GetMetadata()
                value = metadata.get(self.column, "")
                return value if value else ""
        except Exception:
            return ""


class BatchRenamer:
    """Manages component-based batch renaming."""

    def __init__(self, resolve: Any):
        self.resolve = resolve
        self.project = None
        self.media_pool = None
        self.selected_items: list[Any] = []
        self.components: list[Component] = []
        self.metadata_properties: list[str] = []

    def initialize(self) -> bool:
        """Initialize Resolve objects and get selected items."""
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

        # Get selected items
        try:
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
            if metadata:
                self.metadata_properties = list(metadata.keys())
        except Exception:
            self.metadata_properties = []

        return True

    def set_components(self, component_configs: list[dict[str, Any]]) -> None:
        """
        Set components from configuration list.

        Args:
            component_configs: List of component configurations
        """
        self.components = []
        for config in component_configs:
            comp_type = config.get("type", "")

            if comp_type == "Counter":
                self.components.append(CounterComponent(
                    start=config.get("start", 1),
                    padding=config.get("padding", 3),
                    increment=config.get("increment", 1)
                ))
            elif comp_type == "Specified Text":
                self.components.append(SpecifiedTextComponent(
                    text=config.get("text", "")
                ))
            elif comp_type == "Column Data":
                self.components.append(ColumnDataComponent(
                    column=config.get("column", "Name")
                ))

    def generate_new_name(self, item: Any, index: int) -> str:
        """
        Generate new name by applying all components in sequence.

        Args:
            item: Media pool item
            index: Index in selection

        Returns:
            Generated name
        """
        result = ""

        for component in self.components:
            component_output = component.generate(item, index, result)
            result += component_output

        return result if result else item.GetName()

    def preview_changes(self, component_configs: list[dict[str, Any]]) -> list[tuple[str, str]]:
        """
        Preview what names will become with current component configuration.

        Args:
            component_configs: List of component configurations

        Returns:
            List of (original_name, new_name) tuples
        """
        self.set_components(component_configs)
        preview_list: list[tuple[str, str]] = []

        for idx, item in enumerate(self.selected_items):
            original_name = item.GetName()
            new_name = self.generate_new_name(item, idx)
            preview_list.append((original_name, new_name))

        return preview_list

    def apply_batch_rename(self, component_configs: list[dict[str, Any]], verbose: bool = False) -> tuple[bool, str]:
        """
        Apply batch rename with current component configuration.

        Args:
            component_configs: List of component configurations
            verbose: If True, print each rename operation (default: False)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.selected_items:
                return False, "No items selected"

            if not component_configs:
                return False, "No components configured"

            self.set_components(component_configs)

            success_count = 0
            error_count = 0

            for idx, item in enumerate(self.selected_items):
                try:
                    original_name = item.GetName()
                    new_name = self.generate_new_name(item, idx)

                    # Skip if name hasn't changed
                    if new_name == original_name:
                        continue

                    # Apply rename
                    result = item.SetName(new_name)
                    if result:
                        success_count += 1
                        if verbose:
                            print(f"✓ Renamed: '{original_name}' → '{new_name}'")
                    else:
                        error_count += 1
                        if verbose:
                            print(f"✗ Failed: '{original_name}' → '{new_name}'")

                except Exception as e:
                    error_count += 1
                    if verbose:
                        print(f"ERROR processing item: {e}")

            # Build result message
            if success_count > 0:
                message = f"✓ Renamed {success_count} item(s)"
                if error_count > 0:
                    message += f", {error_count} error(s)"
                return True, message
            else:
                return False, f"No items renamed. {error_count} error(s) occurred"

        except Exception as e:
            return False, f"Error: {e}"


class BatchEditDialog:
    """Manages the batch edit dialog UI."""

    MAX_COMPONENTS = 10  # Maximum number of component rows

    # Component type constants
    COMPONENT_TYPES = ["Counter", "Specified Text", "Column Data"]

    # Stack index mapping for component types
    COMPONENT_STACK_INDEX = {
        "Counter": 0,
        "Specified Text": 1,
        "Column Data": 2,
    }

    def __init__(self, resolve: Any, renamer: BatchRenamer):
        self.resolve = resolve
        self.renamer = renamer
        self.fusion = None
        self.ui = None
        self.disp = None
        self.window = None

    def create_dialog(self) -> bool:
        """Create and show the batch edit dialog."""
        try:
            import DaVinciResolveScript

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
            self.disp = DaVinciResolveScript.UIDispatcher(self.ui)

            # Get item count
            item_count = len(self.renamer.selected_items)

            # Build all component rows
            component_rows = []
            for i in range(self.MAX_COMPONENTS):
                component_rows.extend([
                    self.ui.HGroup([
                        self.ui.CheckBox({"ID": f"EnableComponent_{i}", "Text": "", "Checked": (i == 0), "Weight": 0, "MinimumSize": [25, 0]}),
                        self.ui.HGap(5),
                        self.ui.ComboBox({"ID": f"ComponentType_{i}", "Weight": 0, "MinimumSize": [150, 0]}),
                        self.ui.HGap(8),

                        # Stack widget to show only one component type at a time
                        self.ui.Stack({"ID": f"ComponentStack_{i}", "Weight": 1}, [
                            # Index 0: Counter fields
                            self.ui.HGroup([
                                self.ui.HGap(30),
                                self.ui.Label({"Text": "Start:", "Weight": 0, "StyleSheet": "QLabel { padding: 0px; }"}),
                                self.ui.HGap(10),
                                self.ui.SpinBox({"ID": f"CounterStart_{i}", "Value": 1, "Minimum": 0, "Maximum": 9999, "Weight": 0, "MinimumSize": [80, 0]}),
                                self.ui.HGap(25),
                                self.ui.Label({"Text": "Padding:", "Weight": 0, "StyleSheet": "QLabel { padding: 0px; }"}),
                                self.ui.HGap(10),
                                self.ui.SpinBox({"ID": f"CounterPadding_{i}", "Value": 3, "Minimum": 1, "Maximum": 10, "Weight": 0, "MinimumSize": [80, 0]}),
                                self.ui.HGap(40),
                                self.ui.Label({"Text": "Increment:", "Weight": 0, "StyleSheet": "QLabel { padding: 0px; }"}),
                                self.ui.HGap(10),
                                self.ui.SpinBox({"ID": f"CounterIncrement_{i}", "Value": 1, "Minimum": 1, "Maximum": 100, "Weight": 0, "MinimumSize": [80, 0]}),
                            ]),

                            # Index 1: Specified Text field
                            self.ui.LineEdit({"ID": f"SpecifiedText_{i}", "PlaceholderText": "Enter text...", "Weight": 1, "StyleSheet": "QLineEdit { padding: 5px; }"}),

                            # Index 2: Column Data dropdown
                            self.ui.ComboBox({"ID": f"ColumnData_{i}", "Weight": 0, "MinimumSize": [200, 0]}),
                        ]),
                    ]),
                    self.ui.VGap(20),
                ])

            # Create dialog window
            self.window = self.disp.AddWindow({
                "WindowTitle": "Batch Edit - Build Name from Components",
                "ID": "BatchEditDialog",
                "Geometry": [100, 100, 900, 1100],
            }, [
                self.ui.VGroup([
                    # Header
                    self.ui.Label({
                        "Text": f"Build new names for {item_count} selected clip(s)",
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 14, "Bold": True}),
                    }),
                    self.ui.VGap(15),

                    # Instructions
                    self.ui.Label({
                        "Text": "Add components to build clip names. Components are applied in order.",
                        "Weight": 0,
                        "StyleSheet": "QLabel { color: #999; }",
                    }),
                    self.ui.VGap(15),

                ] + component_rows + [

                    # Preview section
                    self.ui.Label({
                        "Text": "Preview:",
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 12, "Bold": True}),
                    }),
                    self.ui.VGap(8),

                    # Preview text area
                    self.ui.TextEdit({
                        "ID": "PreviewText",
                        "ReadOnly": True,
                        "Weight": 0.5,
                        "Font": self.ui.Font({"Family": "Courier", "PixelSize": 11}),
                        "StyleSheet": "QTextEdit { background-color: #2b2b2b; color: #e0e0e0; }",
                    }),

                    self.ui.VGap(15),

                    # Status message
                    self.ui.Label({
                        "ID": "StatusLabel",
                        "Text": "Configure components above and click Preview",
                        "Weight": 0,
                        "StyleSheet": "QLabel { color: #666; }",
                    }),

                    self.ui.VGap(15),

                    # Buttons
                    self.ui.HGroup([
                        self.ui.HGap(0, 1),
                        self.ui.Button({
                            "ID": "PreviewButton",
                            "Text": "Preview",
                            "MinimumSize": [90, 28],
                        }),
                        self.ui.HGap(8),
                        self.ui.Button({
                            "ID": "ApplyButton",
                            "Text": "Apply",
                            "MinimumSize": [90, 28],
                        }),
                        self.ui.HGap(8),
                        self.ui.Button({
                            "ID": "CloseButton",
                            "Text": "Close",
                            "MinimumSize": [90, 28],
                        }),
                    ]),
                ]),
            ])

            # Set up event handlers
            self.window.On.BatchEditDialog.Close = lambda ev: self.on_close(ev)
            self.window.On.CloseButton.Clicked = lambda ev: self.on_close(ev)
            self.window.On.PreviewButton.Clicked = lambda ev: self.on_preview(ev)
            self.window.On.ApplyButton.Clicked = lambda ev: self.on_apply(ev)

            # Set up event handlers for all components
            for i in range(self.MAX_COMPONENTS):
                self.window.On[f"ComponentType_{i}"].CurrentIndexChanged = lambda ev, idx=i: self.on_component_type_changed(ev, idx)
                self.window.On[f"EnableComponent_{i}"].Clicked = lambda ev: self.update_preview()

            # Initialize row widgets with dropdown options
            self.initialize_row_widgets()

            # Initialize UI state for all rows to ensure proper visibility
            for i in range(self.MAX_COMPONENTS):
                self.update_component_ui(i)

            # Show initial preview
            self.update_preview()

            # Show window
            self.window.Show()
            self.disp.RunLoop()
            self.window.Hide()

            return True

        except Exception as e:
            print(f"ERROR: Failed to create dialog: {e}")
            import traceback
            traceback.print_exc()
            return False

    def initialize_row_widgets(self) -> None:
        """Initialize row widgets with options after window is created."""
        itm = self.window.GetItems()
        available_columns = ["Name", "Clip Color"] + self.renamer.metadata_properties

        for i in range(self.MAX_COMPONENTS):
            # Initialize Component Type dropdown
            type_combo = itm[f"ComponentType_{i}"]
            type_combo.AddItems(self.COMPONENT_TYPES)
            type_combo.CurrentIndex = 0

            # Initialize Column Data dropdown
            column_combo = itm[f"ColumnData_{i}"]
            column_combo.AddItems(available_columns)
            if available_columns:
                column_combo.CurrentIndex = 0

    def on_component_type_changed(self, ev: Any, row_index: int) -> None:
        """Handle component type dropdown change."""
        self.update_component_ui(row_index)
        self.update_preview()

    def update_component_ui(self, row_index: int) -> None:
        """Update UI visibility based on component type using Stack widget."""
        itm = self.window.GetItems()
        comp_type = itm[f"ComponentType_{row_index}"].CurrentText

        # Get the Stack widget for this row and set its index
        stack = itm[f"ComponentStack_{row_index}"]
        stack.CurrentIndex = self.COMPONENT_STACK_INDEX.get(comp_type, 0)

    def get_component_configs(self) -> list[dict[str, Any]]:
        """Get component configurations from enabled rows only."""
        itm = self.window.GetItems()
        configs = []

        for i in range(self.MAX_COMPONENTS):
            # Skip if checkbox is not checked
            if not itm[f"EnableComponent_{i}"].Checked:
                continue

            comp_type = itm[f"ComponentType_{i}"].CurrentText

            # Add component based on type
            if comp_type == "Counter":
                configs.append({
                    "type": "Counter",
                    "start": itm[f"CounterStart_{i}"].Value,
                    "padding": itm[f"CounterPadding_{i}"].Value,
                    "increment": itm[f"CounterIncrement_{i}"].Value,
                })
            elif comp_type == "Specified Text":
                # Add specified text (even if empty, user might want empty string)
                configs.append({
                    "type": "Specified Text",
                    "text": itm[f"SpecifiedText_{i}"].Text,
                })
            elif comp_type == "Column Data":
                configs.append({
                    "type": "Column Data",
                    "column": itm[f"ColumnData_{i}"].CurrentText,
                })

        return configs

    def update_preview(self) -> None:
        """Update the preview text area."""
        try:
            itm = self.window.GetItems()
            configs = self.get_component_configs()

            if not configs:
                itm["PreviewText"].PlainText = "No components configured"
                return

            # Get preview list
            preview_list = self.renamer.preview_changes(configs)

            # Build preview text
            preview_lines = []
            max_original_len = max((len(original) for original, _ in preview_list), default=0)

            for original, new_name in preview_list:
                preview_lines.append(f"{original:{max_original_len}} → {new_name}")

            preview_text = "\n".join(preview_lines)
            itm["PreviewText"].PlainText = preview_text

        except Exception as e:
            print(f"ERROR in update_preview: {e}")
            import traceback
            traceback.print_exc()

    def on_preview(self, ev: Any) -> None:
        """Handle Preview button click."""
        try:
            self.update_preview()

            itm = self.window.GetItems()
            itm["StatusLabel"].Text = "✓ Preview updated"
            itm["StatusLabel"].StyleSheet = "QLabel { color: green; }"

        except Exception as e:
            print(f"ERROR in on_preview: {e}")

    def on_apply(self, ev: Any) -> None:
        """Handle Apply button click."""
        try:
            itm = self.window.GetItems()
            configs = self.get_component_configs()

            if not configs:
                itm["StatusLabel"].Text = "ERROR: Add at least one component"
                itm["StatusLabel"].StyleSheet = "QLabel { color: red; }"
                return

            # Apply batch rename
            success, message = self.renamer.apply_batch_rename(configs)

            # Update status
            if success:
                itm["StatusLabel"].Text = message
                itm["StatusLabel"].StyleSheet = "QLabel { color: green; }"
                # Update preview to show applied changes
                self.update_preview()
            else:
                itm["StatusLabel"].Text = message
                itm["StatusLabel"].StyleSheet = "QLabel { color: red; }"

        except Exception as e:
            print(f"ERROR in on_apply: {e}")
            import traceback
            traceback.print_exc()

    def on_close(self, ev: Any) -> None:
        """Handle window close."""
        self.disp.ExitLoop()


def main() -> bool:
    """Main function."""
    print("\n" + "=" * 70)
    print("  Batch Edit - Component-Based Renaming")
    print("=" * 70)

    resolve = get_resolve()
    if not resolve:
        return False

    # Create renamer
    renamer = BatchRenamer(resolve)

    print("\nInitializing...")
    if not renamer.initialize():
        print("ERROR: Failed to initialize")
        return False

    print(f"✓ Found {len(renamer.selected_items)} selected item(s)")
    print(f"✓ Found {len(renamer.metadata_properties)} metadata properties")

    # Create and show dialog
    print("\nOpening dialog...")
    dialog = BatchEditDialog(resolve, renamer)
    dialog.create_dialog()

    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    success: bool = main()
    sys.exit(0 if success else 1)
