#!/usr/bin/env python3.10
"""
Export Stills from Timeline Markers

This script exports still frames from all markers in selected timelines.
Stills are captured to a temporary Gallery album and exported with user-defined naming conventions.

Works in both terminal and Resolve menu contexts.
"""
from __future__ import annotations
from typing import Any
import sys
import os
import traceback
from timecode import Timecode


def add_resolve_module_path() -> bool:
    """
    Add DaVinci Resolve's module path to sys.path.

    Returns:
        True if successful, False otherwise
    """
    import platform
    system = platform.system()

    if system == "Darwin":  # macOS
        module_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    elif system == "Windows":
        module_path = os.path.join(os.environ.get("PROGRAMDATA", ""),
                                   "Blackmagic Design", "DaVinci Resolve",
                                   "Support", "Developer", "Scripting", "Modules")
    elif system == "Linux":
        module_path = "/opt/resolve/Developer/Scripting/Modules/"
    else:
        print(f"ERROR: Unsupported operating system: {system}")
        return False

    if not os.path.exists(module_path):
        print(f"ERROR: DaVinci Resolve Scripting API not found at: {module_path}")
        print("Please ensure DaVinci Resolve is installed correctly.")
        return False

    if module_path not in sys.path:
        sys.path.insert(0, module_path)

    return True


def get_resolve() -> Any | None:
    """
    Get the DaVinci Resolve scripting API object.

    Returns:
        Resolve object if successful, None otherwise
    """
    if not add_resolve_module_path():
        return None

    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")

        if not resolve:
            print("ERROR: Could not connect to DaVinci Resolve.")
            print("Please ensure DaVinci Resolve is running and a project is open.")
            return None

        return resolve

    except ImportError as e:
        print(f"ERROR: Failed to import DaVinciResolveScript: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to get Resolve object: {e}")
        return None


class MarkerStillExporter:
    """
    Exports still frames from timeline markers to a temporary Gallery album.
    """

    # Format mapping: display name -> (extension, API format string)
    FORMAT_MAP = {
        "JPEG": ("jpg", "jpg"),
        "PNG": ("png", "png"),
        "TIFF": ("tif", "tif"),
        "DPX": ("dpx", "dpx"),
    }

    # Default album name for temporary captures
    DEFAULT_ALBUM_NAME = "TempMarkerStills"

    def __init__(self, resolve: Any):
        """
        Initialize the exporter.

        Args:
            resolve: DaVinci Resolve API object
        """
        self.resolve = resolve
        self.project_manager = resolve.GetProjectManager()
        self.project = self.project_manager.GetCurrentProject()
        self.media_pool = self.project.GetMediaPool()
        self.gallery = self.project.GetGallery()
        self.temp_album = None
        self.created_stills = []  # Track stills created by this script

    def get_selected_timelines(self) -> list[Any]:
        """
        Get selected timeline objects from Media Pool.

        Returns:
            List of timeline objects
        """
        # Get selected items from media pool
        selected_items = self.media_pool.GetSelectedClips()  # Correct method!

        if not selected_items:
            print("ERROR: No items selected in Media Pool")
            return []

        # Get timeline names from selected MediaPoolItems
        timeline_names: list[str] = []

        for item in selected_items:
            try:
                # Check if item is a timeline by looking at its properties
                props = item.GetClipProperty()
                if props:
                    # Check if Type indicates it's a timeline
                    item_type = props.get("Type", "")
                    if "Timeline" in str(item_type) or "Compound" in str(item_type):
                        timeline_names.append(item.GetName())
            except Exception:
                continue

        if not timeline_names:
            print("ERROR: No timeline items found in selection")
            print("Please select timeline items (not clips) from the Media Pool")
            return []

        # Get actual Timeline objects from project by matching names
        # Build timeline name-to-object map once (O(n) instead of O(n*m))
        timeline_count = self.project.GetTimelineCount()
        timeline_map: dict[str, Any] = {}

        for idx in range(1, timeline_count + 1):  # 1-based!
            timeline = self.project.GetTimelineByIndex(idx)
            if timeline:
                timeline_map[timeline.GetName()] = timeline

        # Lookup timelines by name
        timelines = [timeline_map[name] for name in timeline_names if name in timeline_map]

        return timelines

    def scan_markers(self, timelines: list[Any]) -> list[tuple[Any, list[tuple[int, dict]]]]:
        """
        Scan all markers in selected timelines.

        Args:
            timelines: List of timeline objects

        Returns:
            List of (timeline, markers) tuples where markers is a list of (frame_id, marker_data) tuples
        """
        timeline_markers = []

        for timeline in timelines:
            markers = timeline.GetMarkers()
            if not markers:
                continue

            # Convert markers dict to sorted list of tuples (sorted by frame_id)
            marker_list = sorted(markers.items())

            timeline_markers.append((timeline, marker_list))

        return timeline_markers

    def create_temp_album(self, album_name: str | None = None) -> Any | None:
        """
        Get the first Gallery still album for capturing stills.

        Note: This method doesn't actually create a new album, it uses the first
        existing album and sets its label.

        Args:
            album_name: Label to set on the album (defaults to DEFAULT_ALBUM_NAME)

        Returns:
            GalleryStillAlbum object or None on failure
        """
        if album_name is None:
            album_name = self.DEFAULT_ALBUM_NAME

        # Get first available album
        albums = self.gallery.GetGalleryStillAlbums()
        if not albums:
            print("ERROR: Could not access Gallery albums")
            return None

        self.temp_album = albums[0]
        self.temp_album.SetLabel(album_name)

        return self.temp_album

    def frame_to_timecode(self, frame: int, timeline: Any, use_timeline_start: bool = True, delimiter: str = "-") -> str:
        """
        Convert frame number to timecode string.

        Args:
            frame: Frame number
            timeline: Timeline object
            use_timeline_start: If True, use timeline's start timecode as base (for display)
                               If False, convert absolute frame directly (for SetCurrentTimecode)
            delimiter: Delimiter to use between timecode components (default "-" for filenames, use ":" for API calls)

        Returns:
            Timecode string in format "HH{delimiter}MM{delimiter}SS{delimiter}FF"
        """
        try:
            # Get timeline properties
            frame_rate = float(timeline.GetSetting("timelineFrameRate"))

            if use_timeline_start:
                # Get timeline's start timecode for proper offset
                start_tc = timeline.GetStartTimecode()
                # Create timecode object from start timecode
                tc = Timecode(frame_rate, start_timecode=start_tc)
                # Add the marker frame offset to the start timecode
                tc.add_frames(frame)
            else:
                # Direct frame to timecode conversion (for SetCurrentTimecode)
                tc = Timecode(frame_rate, frames=frame)

            # Convert to string and apply delimiter
            tc_str = str(tc)
            if delimiter != ":":
                tc_str = tc_str.replace(":", delimiter)

            return tc_str
        except Exception as e:
            print(f"WARNING: Failed to convert frame {frame} to timecode: {e}")
            return f"Frame{frame:06d}"

    def generate_filename(self, timeline: Any, marker_frame: int) -> str:
        """
        Generate filename using timeline name and record timecode.

        Args:
            timeline: Timeline object
            marker_frame: Frame number of marker

        Returns:
            Filename without extension in format: TimelineName_HH-MM-SS-FF
        """
        # Format: TimelineName_RecordTC
        timeline_name = timeline.GetName().replace(" ", "_")
        record_tc = self.frame_to_timecode(marker_frame, timeline)
        return f"{timeline_name}_{record_tc}"

    def capture_stills(self, timeline_markers: list[tuple[Any, list[tuple[int, dict]]]]) -> list[tuple[Any, str]]:
        """
        Capture stills from markers to temporary Gallery album.

        Args:
            timeline_markers: List of (timeline, markers) tuples where markers is list of (frame_id, marker_data)

        Returns:
            List of (still_object, filename) tuples
        """
        captured_stills = []

        for timeline, markers in timeline_markers:
            # Set timeline as current
            self.project.SetCurrentTimeline(timeline)

            # Get timeline start frame for offset calculation
            start_frame = timeline.GetStartFrame()

            for frame_id, marker_data in markers:
                try:
                    # Move playhead to marker position
                    # Add timeline start frame offset to marker position
                    absolute_frame = frame_id + start_frame
                    # For setting playhead: use absolute frame without timeline start offset (needs colon delimiter for API)
                    timeline.SetCurrentTimecode(self.frame_to_timecode(absolute_frame, timeline, use_timeline_start=False, delimiter=":"))

                    # Generate filename (without extension)
                    filename = self.generate_filename(timeline, frame_id)

                    # Capture still to gallery
                    still = timeline.GrabStill()

                    if still:
                        # Store still and filename for later labeling and export
                        captured_stills.append((still, filename))
                        # Track this still for cleanup
                        self.created_stills.append(still)
                    else:
                        print(f"WARNING: Failed to capture still at frame {frame_id} in timeline '{timeline.GetName()}'")

                except Exception as e:
                    print(f"ERROR: Failed to capture still at frame {frame_id}: {e}")
                    continue

        return captured_stills

    def export_stills(self, captured_stills: list[tuple[Any, str]],
                      export_folder: str, format_name: str) -> tuple[int, int]:
        """
        Export stills to folder with selected format.

        Args:
            captured_stills: List of (still_object, filename) tuples
            export_folder: Target export folder
            format_name: Format display name (JPEG, PNG, TIFF, DPX)

        Returns:
            Tuple of (success_count, failure_count)
        """
        if not captured_stills:
            print("ERROR: No stills to export")
            return 0, 0

        if format_name not in self.FORMAT_MAP:
            print(f"ERROR: Invalid format '{format_name}'")
            return 0, 0

        extension, api_format = self.FORMAT_MAP[format_name]

        success_count = 0
        failure_count = 0

        current_album = self.gallery.GetCurrentStillAlbum()

        for still, filename in captured_stills:
            try:
                # Set still label (becomes export filename base)
                current_album.SetLabel(still, filename)

                # Export single still with format
                result = current_album.ExportStills([still], export_folder, "", api_format)

                if result:
                    success_count += 1
                else:
                    failure_count += 1
                    print(f"WARNING: Failed to export still '{filename}'")

            except Exception as e:
                failure_count += 1
                print(f"ERROR: Failed to export still '{filename}': {e}")

        return success_count, failure_count

    def cleanup(self) -> bool:
        """
        Delete temporary Gallery album and its stills.

        Returns:
            True if successful, False otherwise
        """
        if not self.temp_album:
            return True

        try:
            # Delete only the stills created by this script run
            if self.created_stills:
                self.temp_album.DeleteStills(self.created_stills)

            # Clear the list of created stills
            self.created_stills = []

            # Note: Gallery albums cannot be deleted via API
            # We can only delete the stills within the album
            # The album itself will remain (with any pre-existing stills intact)

            return True

        except Exception as e:
            print(f"WARNING: Failed to cleanup temporary album: {e}")
            return False

    def export_from_markers(self, export_folder: str, format_name: str) -> tuple[int, int]:
        """
        Complete workflow: scan, capture, export, cleanup.

        Args:
            export_folder: Target export folder
            format_name: Format display name

        Returns:
            Tuple of (success_count, failure_count)
        """
        try:
            # 1. Get selected timelines
            print("Getting selected timelines...")
            timelines = self.get_selected_timelines()
            if not timelines:
                return 0, 0

            print(f"Found {len(timelines)} timeline(s)")

            # 2. Scan markers
            print("Scanning markers...")
            timeline_markers = self.scan_markers(timelines)
            if not timeline_markers:
                print("ERROR: No markers found in selected timelines")
                return 0, 0

            total_markers = sum(len(markers) for timeline, markers in timeline_markers)
            print(f"Found {total_markers} marker(s)")

            # 3. Create temporary album
            print("Creating temporary Gallery album...")
            album = self.create_temp_album()
            if not album:
                return 0, 0

            # 4. Capture stills
            print("Capturing stills from markers...")
            captured_stills = self.capture_stills(timeline_markers)
            print(f"Captured {len(captured_stills)} still(s)")

            if not captured_stills:
                print("ERROR: No stills were captured")
                self.cleanup()
                return 0, 0

            # 5. Export stills
            print(f"Exporting stills to: {export_folder}")
            success_count, failure_count = self.export_stills(captured_stills, export_folder, format_name)

            # 6. Cleanup
            print("Cleaning up temporary album...")
            self.cleanup()

            return success_count, failure_count

        except Exception as e:
            print(f"ERROR: Export workflow failed: {e}")
            traceback.print_exc()
            self.cleanup()
            return 0, 0


class StillExporterDialog:
    """
    UI dialog for configuring still export settings (Studio version).
    """

    def __init__(self, ui: Any, dispatcher: Any, exporter: MarkerStillExporter):
        """
        Initialize the dialog.

        Args:
            ui: UIManager object
            dispatcher: UIDispatcher object
            exporter: MarkerStillExporter instance
        """
        self.ui = ui
        self.dispatcher = dispatcher
        self.exporter = exporter
        self.window = None
        self.result = None

    def create_dialog(self) -> bool:
        """
        Create and show the dialog window.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create window
            self.window = self.dispatcher.AddWindow(
            {
                "WindowTitle": "Export Stills from Timeline Markers",
                "ID": "ExportStillsDialog",
                "Geometry": [100, 100, 600, 400],
            },
            [
                self.ui.VGroup(
                    [
                        # Instructions
                        self.ui.Label({
                            "ID": "Instructions",
                            "Text": "Export still frames from all markers in selected timelines.\n"
                                   "Select timelines in Media Pool before running.\n"
                                   "Files will be named: TimelineName_HH-MM-SS-FF",
                            "Alignment": {"AlignHCenter": True},
                            "WordWrap": True,
                        }),

                        self.ui.VGap(10),

                        # Export format
                        self.ui.HGroup(
                            [
                                self.ui.Label({"Text": "Export Format:", "Weight": 0.3}),
                                self.ui.ComboBox({
                                    "ID": "ExportFormat",
                                    "Weight": 0.7,
                                }),
                            ]
                        ),

                        # Export folder
                        self.ui.HGroup(
                            [
                                self.ui.Label({"Text": "Export Folder:", "Weight": 0.3}),
                                self.ui.LineEdit({
                                    "ID": "ExportFolder",
                                    "PlaceholderText": "Select export folder...",
                                    "ReadOnly": True,
                                    "Weight": 0.6,
                                }),
                                self.ui.Button({
                                    "ID": "BrowseButton",
                                    "Text": "Browse...",
                                    "Weight": 0.1,
                                }),
                            ]
                        ),

                        self.ui.VGap(10),

                        # Status label
                        self.ui.Label({
                            "ID": "StatusLabel",
                            "Text": "Ready",
                            "Alignment": {"AlignHCenter": True},
                            "StyleSheet": "QLabel { color: green; }",
                        }),

                        self.ui.VGap(10),

                        # Action buttons
                        self.ui.HGroup(
                            [
                                self.ui.Button({"ID": "ExportButton", "Text": "Export"}),
                                self.ui.Button({"ID": "CloseButton", "Text": "Close"}),
                            ]
                        ),
                    ]
                ),
            ]
            )

            # Get window items
            items = self.window.GetItems()

            # Populate format dropdown
            format_combo = items["ExportFormat"]
            for format_name in MarkerStillExporter.FORMAT_MAP.keys():
                format_combo.AddItem(format_name)
            format_combo.SetCurrentIndex(0)  # Default to JPEG

            # Connect button signals
            self.window.On.BrowseButton.Clicked = lambda ev: self.on_browse_clicked(ev)
            self.window.On.ExportButton.Clicked = lambda ev: self.on_export_clicked(ev)
            self.window.On.CloseButton.Clicked = lambda ev: self.on_close_clicked(ev)

            # Show window and run event loop
            self.window.Show()
            self.dispatcher.RunLoop()
            self.window.Hide()

            return True

        except Exception as e:
            print(f"ERROR: Failed to create dialog: {e}")
            traceback.print_exc()
            return False

    def on_browse_clicked(self, ev):
        """Handle Browse button click."""
        # Import tkinter only when needed (UI mode only)
        import tkinter as tk
        from tkinter import filedialog

        # Hide tkinter root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        # Show folder selection dialog
        folder = filedialog.askdirectory(title="Select Export Folder")
        root.destroy()

        if folder:
            items = self.window.GetItems()
            items["ExportFolder"].SetText(folder)

    def on_export_clicked(self, ev):
        """Handle Export button click."""
        items = self.window.GetItems()

        # Validate inputs
        export_format = items["ExportFormat"].CurrentText
        export_folder = items["ExportFolder"].GetText()

        if not export_folder:
            items["StatusLabel"].SetText("ERROR: Please select export folder")
            items["StatusLabel"].SetStyleSheet("QLabel { color: red; }")
            return

        if not os.path.isdir(export_folder):
            items["StatusLabel"].SetText("ERROR: Export folder does not exist")
            items["StatusLabel"].SetStyleSheet("QLabel { color: red; }")
            return

        # Update status
        items["StatusLabel"].SetText("Exporting...")
        items["StatusLabel"].SetStyleSheet("QLabel { color: blue; }")

        # Execute export
        success_count, failure_count = self.exporter.export_from_markers(
            export_folder, export_format
        )

        # Update status with results
        if success_count > 0:
            items["StatusLabel"].SetText(
                f"Success: Exported {success_count} still(s) ({failure_count} failed)"
            )
            items["StatusLabel"].SetStyleSheet("QLabel { color: green; }")
        else:
            items["StatusLabel"].SetText(f"ERROR: Export failed ({failure_count} errors)")
            items["StatusLabel"].SetStyleSheet("QLabel { color: red; }")

    def on_close_clicked(self, ev):
        """Handle Close button click."""
        self.dispatcher.ExitLoop()


def run_with_ui(resolve: Any) -> bool:
    """
    Run script with UI dialog (Studio version).

    Args:
        resolve: DaVinci Resolve API object

    Returns:
        True if successful, False otherwise
    """
    try:
        # Import DaVinciResolveScript for UIDispatcher
        import DaVinciResolveScript

        # Get Fusion and UIManager
        fusion = resolve.Fusion()
        if not fusion:
            print("ERROR: Could not access Fusion")
            print("Falling back to console mode...")
            return run_console_mode(resolve)

        ui = fusion.UIManager  # Property, not method
        if not ui:
            print("ERROR: UIManager not available (requires DaVinci Resolve Studio)")
            print("Falling back to console mode...")
            return run_console_mode(resolve)

        # Create UIDispatcher instance
        dispatcher = DaVinciResolveScript.UIDispatcher(ui)

        # Create exporter
        exporter = MarkerStillExporter(resolve)

        # Create and show dialog
        dialog = StillExporterDialog(ui, dispatcher, exporter)
        return dialog.create_dialog()  # Returns bool, does everything

    except Exception as e:
        print(f"ERROR: UI mode failed: {e}")
        traceback.print_exc()
        return False


def run_console_mode(resolve: Any) -> bool:
    """
    Run script in console mode (Free version fallback).

    Args:
        resolve: DaVinci Resolve API object

    Returns:
        True if successful, False otherwise
    """
    print("\n=== Export Stills from Timeline Markers (Console Mode) ===\n")

    try:
        # Create exporter
        exporter = MarkerStillExporter(resolve)

        # Get selected timelines
        print("Checking selected timelines...")
        timelines = exporter.get_selected_timelines()
        if not timelines:
            return False

        # Scan markers
        print("Scanning markers...")
        timeline_markers = exporter.scan_markers(timelines)
        if not timeline_markers:
            print("ERROR: No markers found in selected timelines")
            return False

        total_markers = sum(len(markers) for timeline, markers in timeline_markers)
        print(f"\nFound {len(timelines)} timeline(s) with {total_markers} marker(s)")

        # Show preview
        for timeline, markers in timeline_markers:
            print(f"  - {timeline.GetName()}: {len(markers)} marker(s)")

        # Get user input
        print("\nExport Format:")
        formats = list(MarkerStillExporter.FORMAT_MAP.keys())
        for i, fmt in enumerate(formats, 1):
            print(f"  {i}. {fmt}")

        format_choice = input(f"Select format (1-{len(formats)}): ").strip()
        try:
            format_index = int(format_choice) - 1
            if format_index < 0 or format_index >= len(formats):
                raise ValueError
            format_name = formats[format_index]
        except:
            print("ERROR: Invalid choice")
            return False

        export_folder = input("\nEnter export folder path: ").strip()
        if not export_folder or not os.path.isdir(export_folder):
            print("ERROR: Invalid folder path")
            return False

        # Execute export
        print("\nStarting export...")
        success_count, failure_count = exporter.export_from_markers(
            export_folder, format_name
        )

        # Show results
        print(f"\n=== Export Complete ===")
        print(f"Success: {success_count} still(s)")
        print(f"Failed: {failure_count} still(s)")

        return success_count > 0

    except Exception as e:
        print(f"ERROR: Console mode failed: {e}")
        traceback.print_exc()
        return False


def main() -> bool:
    """
    Main function.

    Returns:
        True if successful, False if an error occurred
    """
    try:
        # Connect to Resolve
        resolve = get_resolve()
        if not resolve:
            return False

        # Try UI mode first, fallback to console
        # Note: Project validation is handled within the exporter methods
        return run_with_ui(resolve)

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success: bool = main()
    sys.exit(0 if success else 1)
