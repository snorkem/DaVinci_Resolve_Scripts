#!/usr/bin/env python3.10
"""
Add LUTs by Rules - Apply LUTs to timeline clips based on property matching

This script scans selected timelines to discover clip properties (codec,
resolution, frame rate, clip color), then allows users to create rules that
automatically apply LUTs to clips matching those properties.

Works in both terminal and Resolve menu contexts.
Requires DaVinci Resolve Studio for UI dialogs (console fallback for Free version).
"""
from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
import sys
import os
import platform


# ============================================================================
# RESOLVE CONNECTION (Inline - no external imports needed)
# ============================================================================

def add_resolve_module_path() -> bool:
    """Add DaVinci Resolve's module path to sys.path based on OS."""
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
            print("       Make sure DaVinci Resolve is running.")
            return None
        return resolve
    except Exception as e:
        print(f"ERROR: {e}")
        return None


# ============================================================================
# PROJECT SCANNER - Discovers property values from selected timelines
# ============================================================================

class ProjectScanner:
    """Scans selected timelines to discover available property values."""

    def __init__(self, timelines: list[Any]):
        self.timelines = timelines
        self.discovered: dict[str, set[str]] = {
            "codecs": set(),
            "resolutions": set(),
            "frame_rates": set(),
            "clip_colors": set(),
        }

    def scan_timelines(self) -> bool:
        """
        Scan selected timelines and collect property values.

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.timelines:
                print("WARNING: No timelines provided")
                return False

            print(f"Scanning {len(self.timelines)} selected timeline(s) for clip properties...")

            for timeline in self.timelines:
                timeline_name = timeline.GetName()
                print(f"  Scanning: {timeline_name}")

                # Scan all video tracks
                video_track_count = timeline.GetTrackCount("video")
                for track_idx in range(1, video_track_count + 1):
                    items = timeline.GetItemListInTrack("video", track_idx)

                    for item in items:
                        self._extract_properties_from_item(item)

            # Report findings
            print(f"\nDiscovered properties:")
            print(f"  Codecs: {len(self.discovered['codecs'])}")
            print(f"  Resolutions: {len(self.discovered['resolutions'])}")
            print(f"  Frame Rates: {len(self.discovered['frame_rates'])}")
            print(f"  Clip Colors: {len(self.discovered['clip_colors'])}")

            return True

        except Exception as e:
            print(f"ERROR scanning timelines: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_properties_from_item(self, item: Any) -> None:
        """Extract and store properties from a timeline item."""
        try:
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return

            # Get all properties at once
            props = media_pool_item.GetClipProperty()
            if not props:
                return

            # Extract codec
            codec = props.get("Video Codec", "")
            if codec and codec.strip():
                self.discovered["codecs"].add(codec.strip())

            # Extract resolution
            resolution = props.get("Resolution", "")
            if resolution and str(resolution).strip():
                self.discovered["resolutions"].add(str(resolution).strip())

            # Extract frame rate
            frame_rate = props.get("Frame Rate", "") or props.get("FPS", "")
            if frame_rate:
                # Normalize frame rate using helper function
                normalized_fps = normalize_frame_rate(frame_rate)
                self.discovered["frame_rates"].add(normalized_fps)

            # Extract clip color (from timeline item, not media pool item)
            clip_color = item.GetClipColor()
            if clip_color and clip_color.strip():
                self.discovered["clip_colors"].add(clip_color.strip())

        except Exception:
            # Silently skip items that can't be read
            pass

    def get_discovered_values(self) -> dict[str, list[str]]:
        """
        Get discovered values as sorted lists.

        Returns:
            Dictionary with sorted lists of values
        """
        return {
            "codecs": sorted(list(self.discovered["codecs"])),
            "resolutions": sorted(list(self.discovered["resolutions"])),
            "frame_rates": sorted(list(self.discovered["frame_rates"])),
            "clip_colors": sorted(list(self.discovered["clip_colors"])),
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_frame_rate(frame_rate: str | int | float) -> str:
    """
    Normalize frame rate to consistent string format.

    Converts numeric frame rates to 3-decimal precision strings and strips
    trailing zeros for cleaner display (e.g., 24.000 -> "24", 23.976 -> "23.976").

    Args:
        frame_rate: Frame rate as string, int, or float

    Returns:
        Normalized frame rate string

    Examples:
        >>> normalize_frame_rate(24.0)
        '24'
        >>> normalize_frame_rate(23.976)
        '23.976'
        >>> normalize_frame_rate("29.97")
        '29.97'
        >>> normalize_frame_rate(60)
        '60'
    """
    try:
        # Convert to float if not already
        fps = float(frame_rate)
        # Format to 3 decimals, strip trailing zeros and decimal point
        normalized = f"{fps:.3f}".rstrip('0').rstrip('.')
        return normalized
    except (ValueError, TypeError):
        # Return as-is if can't convert (already a clean string)
        return str(frame_rate).strip()


# ============================================================================
# RULE CLASSES - Match clip properties
# ============================================================================

class Rule(ABC):
    """Abstract base class for property matching rules."""

    def __init__(self, value: str, lut_path: str, target_node: int):
        self.value = value
        self.lut_path = lut_path
        self.target_node = target_node

    @abstractmethod
    def matches(self, item: Any) -> bool:
        """Check if timeline item matches this rule."""
        pass

    @abstractmethod
    def get_property_value(self, item: Any) -> str:
        """Get the property value from the item for display purposes."""
        pass


class CodecRule(Rule):
    """Match clips by video codec (exact match)."""

    def matches(self, item: Any) -> bool:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return False

            codec = media_pool_item.GetClipProperty("Video Codec")
            if not codec:
                return False

            return codec == self.value
        except Exception:
            return False

    def get_property_value(self, item: Any) -> str:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if media_pool_item:
                return media_pool_item.GetClipProperty("Video Codec") or ""
        except Exception:
            pass
        return ""


class ResolutionRule(Rule):
    """Match clips by resolution (exact match)."""

    def matches(self, item: Any) -> bool:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return False

            props = media_pool_item.GetClipProperty()
            resolution = props.get("Resolution", "")

            if not resolution:
                return False

            return str(resolution).strip() == self.value
        except Exception:
            return False

    def get_property_value(self, item: Any) -> str:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if media_pool_item:
                props = media_pool_item.GetClipProperty()
                resolution = props.get("Resolution", "")
                if resolution:
                    return str(resolution).strip()
        except Exception:
            pass
        return ""


class FrameRateRule(Rule):
    """Match clips by frame rate (exact match)."""

    def matches(self, item: Any) -> bool:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return False

            props = media_pool_item.GetClipProperty()
            frame_rate = props.get("Frame Rate", "") or props.get("FPS", "")

            if not frame_rate:
                return False

            # Normalize using helper function
            normalized_fps = normalize_frame_rate(frame_rate)
            return normalized_fps == self.value
        except Exception:
            return False

    def get_property_value(self, item: Any) -> str:
        try:
            media_pool_item = item.GetMediaPoolItem()
            if media_pool_item:
                props = media_pool_item.GetClipProperty()
                frame_rate = props.get("Frame Rate", "") or props.get("FPS", "")
                if frame_rate:
                    # Normalize using helper function
                    return normalize_frame_rate(frame_rate)
        except Exception:
            pass
        return ""


class ClipColorRule(Rule):
    """Match clips by clip color marker (exact match)."""

    def matches(self, item: Any) -> bool:
        try:
            # Only match media-based clips (skip generators, titles, etc.)
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return False

            clip_color = item.GetClipColor()
            if not clip_color:
                return False

            return clip_color == self.value
        except Exception:
            return False

    def get_property_value(self, item: Any) -> str:
        try:
            return item.GetClipColor() or ""
        except Exception:
            pass
        return ""


# ============================================================================
# LUT MANAGER - Scans and manages available LUTs
# ============================================================================

class LUTManager:
    """Manages LUT file discovery and validation."""

    def __init__(self):
        self.lut_folders: list[str] = []
        self.available_luts: list[str] = []
        self._setup_lut_folders()

    def _setup_lut_folders(self) -> None:
        """Setup LUT folder paths based on OS."""
        os_name = platform.system()

        if os_name == "Darwin":  # macOS
            self.lut_folders = [
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/",
                os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/User/LUT/"),
            ]
        elif os_name == "Windows":
            programdata = os.environ.get('PROGRAMDATA', 'C:/ProgramData')
            appdata = os.environ.get('APPDATA', '')
            self.lut_folders = [
                os.path.join(programdata, "Blackmagic Design", "DaVinci Resolve", "LUT"),
                os.path.join(appdata, "Blackmagic Design", "DaVinci Resolve", "LUT"),
            ]
        elif os_name == "Linux":
            self.lut_folders = [
                "/opt/resolve/LUT/",
                os.path.expanduser("~/.local/share/DaVinciResolve/LUT/"),
            ]

    def scan_luts(self) -> list[str]:
        """
        Recursively scan LUT folders and all subfolders for available LUT files.
        Supported formats: .cube, .3dl, .ilut, .dat

        Returns:
            List of full paths to LUT files
        """
        self.available_luts = []

        for folder in self.lut_folders:
            if not os.path.exists(folder):
                continue

            try:
                # os.walk() recursively traverses all subdirectories
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(('.cube', '.3dl', '.ilut', '.dat')):
                            full_path = os.path.join(root, file)
                            self.available_luts.append(full_path)
            except Exception as e:
                print(f"WARNING: Could not scan {folder}: {e}")

        return sorted(self.available_luts)

    def get_lut_display_names(self) -> list[str]:
        """
        Get display names for LUTs (filename with extension), sorted alphabetically.
        Includes a "(None - Remove LUT)" option as the first item.

        Returns:
            List of display names with removal option first, then sorted LUT files
        """
        lut_names = sorted([os.path.basename(lut) for lut in self.available_luts])
        return ["(None - Remove LUT)"] + lut_names

    def get_lut_path_by_display_name(self, display_name: str) -> str | None:
        """
        Get full path by display name.

        Args:
            display_name: Display name (filename), or "(None - Remove LUT)" for removal

        Returns:
            Full path, empty string for removal option, or None if not found
        """
        # Special case: removal option returns empty string
        if display_name == "(None - Remove LUT)":
            return ""

        # Regular LUT lookup
        for lut in self.available_luts:
            if os.path.basename(lut) == display_name:
                return lut
        return None

    def validate_lut_path(self, path: str) -> bool:
        """
        Check if LUT path is valid.

        Args:
            path: File path to LUT, or empty string for removal

        Returns:
            True if path is valid (exists with correct extension) or empty (removal)
        """
        # Empty path is valid - indicates LUT removal
        if path == "":
            return True

        # Regular LUT file validation
        if not path or not os.path.exists(path):
            return False
        return path.lower().endswith(('.cube', '.3dl', '.ilut', '.dat'))


# ============================================================================
# LUT APPLIER - Applies LUTs based on rules
# ============================================================================

class LUTApplier:
    """Applies LUTs to timeline clips based on matching rules."""

    def __init__(self, resolve: Any, timelines: list[Any], rules: list[Rule]):
        self.resolve = resolve
        self.timelines = timelines
        self.rules = rules
        self.results: dict[str, Any] = {
            "clips_processed": 0,
            "clips_skipped": 0,
            "luts_applied": 0,
            "errors": 0,
            "details": []
        }

    def apply_luts(self, verbose: bool = False) -> dict[str, Any]:
        """
        Apply LUTs to clips in timelines based on rules.

        Args:
            verbose: If True, print detailed progress

        Returns:
            Results dictionary with counts and details
        """
        if not self.rules:
            print("WARNING: No rules configured")
            return self.results

        for timeline in self.timelines:
            timeline_name = timeline.GetName()
            if verbose:
                print(f"\nProcessing timeline: {timeline_name}")

            # Process all video tracks
            video_track_count = timeline.GetTrackCount("video")

            for track_idx in range(1, video_track_count + 1):
                items = timeline.GetItemListInTrack("video", track_idx)

                for item in items:
                    self.results["clips_processed"] += 1
                    self._process_item(item, timeline_name, verbose)

        return self.results

    def _process_item(self, item: Any, timeline_name: str, verbose: bool) -> None:
        """Process a single timeline item against all rules."""
        item_name = item.GetName()

        # Check if this is a non-media clip (generator, title, etc.)
        try:
            media_pool_item = item.GetMediaPoolItem()
            is_media_clip = media_pool_item is not None
        except Exception:
            is_media_clip = False

        # If non-media clip, skip silently
        if not is_media_clip:
            self.results["clips_skipped"] += 1
            if verbose:
                print(f"  ⊘ Skipped (generator/title): {item_name}")
            return

        # Check item against all rules
        matched_any_rule = False
        for rule in self.rules:
            if rule.matches(item):
                matched_any_rule = True
                # Rule matches - apply or remove LUT
                success, status_msg = self._apply_lut_to_item(item, rule)

                # Detect if this is a removal operation
                is_removal = (rule.lut_path == "")
                property_value = rule.get_property_value(item)

                if success:
                    self.results["luts_applied"] += 1

                    if is_removal:
                        # LUT removal
                        if verbose:
                            print(f"  ✓ Removed LUT from node {rule.target_node}: {item_name} ({property_value})")

                        self.results["details"].append({
                            "timeline": timeline_name,
                            "clip": item_name,
                            "property": property_value,
                            "lut": "(Removed)",
                            "target_node": rule.target_node,
                            "success": True
                        })
                    else:
                        # LUT application
                        lut_name = os.path.basename(rule.lut_path)
                        if verbose:
                            print(f"  ✓ Applied {lut_name} to: {item_name} ({property_value})")

                        self.results["details"].append({
                            "timeline": timeline_name,
                            "clip": item_name,
                            "property": property_value,
                            "lut": lut_name,
                            "target_node": rule.target_node,
                            "success": True
                        })
                else:
                    self.results["errors"] += 1
                    action = "remove LUT from" if is_removal else "apply LUT to"
                    if verbose:
                        print(f"  ✗ Failed to {action}: {item_name}")
                        print(f"     Reason: {status_msg}")

                    self.results["details"].append({
                        "timeline": timeline_name,
                        "clip": item_name,
                        "lut": "(Removed)" if is_removal else os.path.basename(rule.lut_path),
                        "target_node": rule.target_node,
                        "error": status_msg,
                        "success": False
                    })

                # Only apply first matching rule
                break

    def _apply_lut_to_item(self, item: Any, rule: Rule) -> tuple[bool, str]:
        """
        Apply or remove LUT from a timeline item at specified node.

        Args:
            item: Timeline item
            rule: Rule containing LUT path (empty string = remove) and target node

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            # 0. Check if clip supports color grading (defensive check)
            media_pool_item = item.GetMediaPoolItem()
            if not media_pool_item:
                return False, "Clip is a generator/title (no color grading support)"

            # 1. Validate graph access
            graph = item.GetNodeGraph(1)
            if not graph:
                return False, "Failed to get node graph (layer 1)"

            # 2. Check node count
            node_count = graph.GetNumNodes()
            if node_count is None:
                return False, "Failed to get node count from graph"

            # 3. Validate target node is within range
            if rule.target_node < 1:
                return False, f"Invalid target node {rule.target_node} (must be >= 1)"

            if rule.target_node > node_count:
                return False, f"Target node {rule.target_node} out of range (clip has {node_count} node(s)). Add nodes in Color page or change target node."

            # 4. Detect LUT removal vs application
            is_removal = (rule.lut_path == "")

            if not is_removal:
                # 5. Verify LUT file exists (only for application, not removal)
                if not os.path.exists(rule.lut_path):
                    return False, f"LUT file not found: {rule.lut_path}"

                # 6. Check if file is readable
                if not os.access(rule.lut_path, os.R_OK):
                    return False, f"LUT file not readable: {rule.lut_path}"

            # 7. Attempt to apply/remove LUT (1-based indexing!)
            result = graph.SetLUT(rule.target_node, rule.lut_path)

            if not result:
                if is_removal:
                    return False, f"SetLUT() returned False (failed to remove LUT from node {rule.target_node})"
                else:
                    return False, f"SetLUT() returned False (Resolve rejected the LUT file). Check LUT format and validity."

            return True, "Removed" if is_removal else "Applied"

        except Exception as e:
            # Capture the actual exception for debugging
            import traceback
            error_details = traceback.format_exc()
            return False, f"Exception: {str(e)}"

    def preview_matches(self) -> list[dict[str, str]]:
        """
        Preview which clips would be affected by rules.

        Returns:
            List of dicts with clip info and matching rules
        """
        matches: list[dict[str, str]] = []

        for timeline in self.timelines:
            timeline_name = timeline.GetName()

            # Process all video tracks
            video_track_count = timeline.GetTrackCount("video")

            for track_idx in range(1, video_track_count + 1):
                items = timeline.GetItemListInTrack("video", track_idx)

                for item in items:
                    item_name = item.GetName()

                    # Check against all rules
                    for rule in self.rules:
                        if rule.matches(item):
                            property_value = rule.get_property_value(item)
                            # Handle removal vs application
                            if rule.lut_path == "":
                                lut_name = "(Remove LUT)"
                            else:
                                lut_name = os.path.basename(rule.lut_path)

                            matches.append({
                                "timeline": timeline_name,
                                "clip": item_name,
                                "property": property_value,
                                "lut": lut_name
                            })

                            # Only first matching rule
                            break

        return matches


# ============================================================================
# DIALOG UI - Studio version with UIManager
# ============================================================================

class AddLUTDialog:
    """Manages the Add LUTs by Rules dialog UI."""

    MAX_RULES = 10  # Maximum number of rule rows

    # Rule type constants
    RULE_TYPES = ["Codec", "Resolution", "Frame Rate", "Clip Color"]

    # Stack index mapping for rule types
    RULE_STACK_INDEX = {
        "Codec": 0,
        "Resolution": 1,
        "Frame Rate": 2,
        "Clip Color": 3,
    }

    # Widget ID suffix mapping for rule types
    RULE_VALUE_WIDGETS = {
        "Codec": "CodecValue",
        "Resolution": "ResolutionValue",
        "Frame Rate": "FrameRateValue",
        "Clip Color": "ClipColorValue",
    }

    # Rule class mapping for rule types
    RULE_CLASSES = {
        "Codec": CodecRule,
        "Resolution": ResolutionRule,
        "Frame Rate": FrameRateRule,
        "Clip Color": ClipColorRule,
    }

    def __init__(self, resolve: Any, timelines: list[Any], discovered_values: dict[str, list[str]], lut_manager: LUTManager):
        self.resolve = resolve
        self.timelines = timelines
        self.discovered_values = discovered_values
        self.lut_manager = lut_manager
        self.fusion = None
        self.ui = None
        self.disp = None
        self.window = None

    def create_dialog(self) -> bool:
        """Create and show the Add LUTs by Rules dialog."""
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

            # Get timeline count
            timeline_count = len(self.timelines)

            # Build all rule rows
            rule_rows = []
            for i in range(self.MAX_RULES):
                rule_rows.extend([
                    self.ui.HGroup([
                        self.ui.CheckBox({"ID": f"EnableRule_{i}", "Text": "", "Checked": (i == 0), "Weight": 0, "MinimumSize": [25, 0]}),
                        self.ui.HGap(5),
                        self.ui.Label({"Text": f"Rule {i+1}:", "Weight": 0, "MinimumSize": [50, 0]}),
                        self.ui.HGap(5),
                        self.ui.ComboBox({"ID": f"RuleType_{i}", "Weight": 0, "MinimumSize": [120, 0]}),
                        self.ui.HGap(8),

                        # Stack widget to show property-specific dropdown
                        self.ui.Stack({"ID": f"PropertyStack_{i}", "Weight": 0}, [
                            # Index 0: Codec dropdown
                            self.ui.ComboBox({"ID": f"CodecValue_{i}", "Weight": 0, "MinimumSize": [180, 0]}),

                            # Index 1: Resolution dropdown
                            self.ui.ComboBox({"ID": f"ResolutionValue_{i}", "Weight": 0, "MinimumSize": [180, 0]}),

                            # Index 2: Frame Rate dropdown
                            self.ui.ComboBox({"ID": f"FrameRateValue_{i}", "Weight": 0, "MinimumSize": [180, 0]}),

                            # Index 3: Clip Color dropdown
                            self.ui.ComboBox({"ID": f"ClipColorValue_{i}", "Weight": 0, "MinimumSize": [180, 0]}),
                        ]),

                        self.ui.HGap(8),
                        self.ui.ComboBox({"ID": f"LUTValue_{i}", "Weight": 1, "MinimumSize": [200, 0]}),
                        self.ui.HGap(8),
                        self.ui.Label({"Text": "Node:", "Weight": 0}),
                        self.ui.SpinBox({"ID": f"NodeValue_{i}", "Value": 1, "Minimum": 1, "Maximum": 10, "Weight": 0, "MinimumSize": [60, 0]}),
                    ]),
                    self.ui.VGap(15),
                ])

            # Create dialog window
            self.window = self.disp.AddWindow({
                "WindowTitle": "Add LUTs by Rules",
                "ID": "AddLUTDialog",
                "Geometry": [100, 100, 1200, 900],
            }, [
                self.ui.VGroup([
                    # Header
                    self.ui.Label({
                        "Text": f"Apply LUTs to {timeline_count} selected timeline(s)",
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 14, "Bold": True}),
                    }),
                    self.ui.VGap(10),

                    # Instructions
                    self.ui.Label({
                        "Text": "Configure rules to match clip properties and apply LUTs. Properties discovered by scanning selected timelines.",
                        "Weight": 0,
                        "StyleSheet": "QLabel { color: #999; }",
                    }),
                    self.ui.VGap(15),

                    # Rule configuration section
                    self.ui.Label({
                        "Text": "Rules:",
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 12, "Bold": True}),
                    }),
                    self.ui.VGap(10),

                ] + rule_rows + [

                    # Preview section
                    self.ui.Label({
                        "Text": "Preview (clips that will be affected):",
                        "Weight": 0,
                        "Font": self.ui.Font({"PixelSize": 12, "Bold": True}),
                    }),
                    self.ui.VGap(8),

                    # Preview text area
                    self.ui.TextEdit({
                        "ID": "PreviewText",
                        "ReadOnly": True,
                        "Weight": 1,
                        "Font": self.ui.Font({"Family": "Courier", "PixelSize": 11}),
                        "StyleSheet": "QTextEdit { background-color: #2b2b2b; color: #e0e0e0; }",
                    }),

                    self.ui.VGap(15),

                    # Status message
                    self.ui.Label({
                        "ID": "StatusLabel",
                        "Text": "Configure rules above and click Preview",
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
            self.window.On.AddLUTDialog.Close = lambda ev: self.on_close(ev)
            self.window.On.CloseButton.Clicked = lambda ev: self.on_close(ev)
            self.window.On.PreviewButton.Clicked = lambda ev: self.on_preview(ev)
            self.window.On.ApplyButton.Clicked = lambda ev: self.on_apply(ev)

            # Set up event handlers for all rules
            for i in range(self.MAX_RULES):
                self.window.On[f"RuleType_{i}"].CurrentIndexChanged = lambda ev, idx=i: self.on_rule_type_changed(ev, idx)
                self.window.On[f"EnableRule_{i}"].Clicked = lambda ev: self.update_preview()

            # Initialize row widgets with dropdown options
            self.initialize_row_widgets()

            # Initialize UI state for all rows
            for i in range(self.MAX_RULES):
                self.update_rule_ui(i)

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

        # Get LUT display names
        lut_names = self.lut_manager.get_lut_display_names()
        if not lut_names:
            lut_names = ["(No LUTs found)"]

        for i in range(self.MAX_RULES):
            # Initialize Rule Type dropdown
            rule_combo = itm[f"RuleType_{i}"]
            rule_combo.AddItems(self.RULE_TYPES)
            rule_combo.CurrentIndex = 0

            # Initialize property value dropdowns
            # Codec
            codec_combo = itm[f"CodecValue_{i}"]
            codecs = self.discovered_values.get("codecs", [])
            if codecs:
                codec_combo.AddItems(codecs)
                codec_combo.CurrentIndex = 0
            else:
                codec_combo.AddItems(["(No codecs found)"])

            # Resolution
            resolution_combo = itm[f"ResolutionValue_{i}"]
            resolutions = self.discovered_values.get("resolutions", [])
            if resolutions:
                resolution_combo.AddItems(resolutions)
                resolution_combo.CurrentIndex = 0
            else:
                resolution_combo.AddItems(["(No resolutions found)"])

            # Frame Rate
            framerate_combo = itm[f"FrameRateValue_{i}"]
            framerates = self.discovered_values.get("frame_rates", [])
            if framerates:
                framerate_combo.AddItems(framerates)
                framerate_combo.CurrentIndex = 0
            else:
                framerate_combo.AddItems(["(No frame rates found)"])

            # Clip Color
            clipcolor_combo = itm[f"ClipColorValue_{i}"]
            clipcolors = self.discovered_values.get("clip_colors", [])
            if clipcolors:
                clipcolor_combo.AddItems(clipcolors)
                clipcolor_combo.CurrentIndex = 0
            else:
                clipcolor_combo.AddItems(["(No clip colors found)"])

            # Initialize LUT dropdown
            lut_combo = itm[f"LUTValue_{i}"]
            lut_combo.AddItems(lut_names)
            if lut_names:
                lut_combo.CurrentIndex = 0

    def on_rule_type_changed(self, ev: Any, row_index: int) -> None:
        """Handle rule type dropdown change."""
        self.update_rule_ui(row_index)
        self.update_preview()

    def update_rule_ui(self, row_index: int) -> None:
        """Update UI visibility based on rule type using Stack widget."""
        itm = self.window.GetItems()
        rule_type = itm[f"RuleType_{row_index}"].CurrentText

        # Get the Stack widget for this row and set its index
        stack = itm[f"PropertyStack_{row_index}"]
        stack.CurrentIndex = self.RULE_STACK_INDEX.get(rule_type, 0)

    def get_rule_configs(self) -> list[Rule]:
        """Get configured rules from enabled rows."""
        itm = self.window.GetItems()
        rules: list[Rule] = []

        for i in range(self.MAX_RULES):
            # Skip if checkbox is not checked
            if not itm[f"EnableRule_{i}"].Checked:
                continue

            rule_type = itm[f"RuleType_{i}"].CurrentText
            target_node = itm[f"NodeValue_{i}"].Value

            # Get property value based on rule type (using mapping)
            widget_suffix = self.RULE_VALUE_WIDGETS.get(rule_type)
            if not widget_suffix:
                continue
            value = itm[f"{widget_suffix}_{i}"].CurrentText

            # Get LUT path
            lut_display_name = itm[f"LUTValue_{i}"].CurrentText
            lut_path = self.lut_manager.get_lut_path_by_display_name(lut_display_name)

            # Skip if lookup failed (None), but allow empty string (removal operation)
            if lut_path is None:
                continue

            # Validate LUT path
            if not self.lut_manager.validate_lut_path(lut_path):
                continue

            # Create appropriate rule object (using mapping)
            rule_class = self.RULE_CLASSES.get(rule_type)
            if rule_class:
                rules.append(rule_class(value, lut_path, target_node))

        return rules

    def update_preview(self) -> None:
        """Update the preview text area."""
        try:
            itm = self.window.GetItems()
            rules = self.get_rule_configs()

            if not rules:
                itm["PreviewText"].PlainText = "No rules configured"
                return

            # Get preview matches
            applier = LUTApplier(self.resolve, self.timelines, rules)
            matches = applier.preview_matches()

            if not matches:
                itm["PreviewText"].PlainText = "No clips match the configured rules"
                return

            # Build preview text
            preview_lines = []
            preview_lines.append(f"Found {len(matches)} clip(s) that will be affected:\n")

            for match in matches:
                preview_lines.append(f"Timeline: {match['timeline']}")
                preview_lines.append(f"  Clip: {match['clip']}")
                preview_lines.append(f"  Property: {match['property']}")
                preview_lines.append(f"  LUT: {match['lut']}")
                preview_lines.append("")

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
            rules = self.get_rule_configs()

            if not rules:
                itm["StatusLabel"].Text = "ERROR: Add at least one rule"
                itm["StatusLabel"].StyleSheet = "QLabel { color: red; }"
                return

            # Apply LUTs
            applier = LUTApplier(self.resolve, self.timelines, rules)
            results = applier.apply_luts(verbose=True)

            # Update status
            message = f"✓ Processed {results['clips_processed']} clips, applied {results['luts_applied']} LUTs"

            # Add skip count if any
            if results['clips_skipped'] > 0:
                message += f", skipped {results['clips_skipped']} (generators/titles)"

            if results['errors'] > 0:
                message += f", {results['errors']} error(s)"

                # Show first error reason in status
                error_details = [d for d in results['details'] if not d.get('success', True)]
                if error_details:
                    first_error = error_details[0]
                    error_reason = first_error.get('error', 'Unknown error')
                    message += f"\nFirst error: {error_reason}"
                    if len(error_details) > 1:
                        message += f"\n(See console for all {len(error_details)} error details)"

                itm["StatusLabel"].StyleSheet = "QLabel { color: orange; }"
            else:
                itm["StatusLabel"].StyleSheet = "QLabel { color: green; }"

            itm["StatusLabel"].Text = message

            # Update preview to show what was done
            self.update_preview()

        except Exception as e:
            print(f"ERROR in on_apply: {e}")
            import traceback
            traceback.print_exc()

    def on_close(self, ev: Any) -> None:
        """Handle window close."""
        self.disp.ExitLoop()


# ============================================================================
# CONSOLE FALLBACK - For Resolve Free version
# ============================================================================

def console_mode(resolve: Any, timelines: list[Any], discovered_values: dict[str, list[str]], lut_manager: LUTManager) -> bool:
    """
    Console-based mode for Resolve Free version.

    Args:
        resolve: Resolve API object
        timelines: List of timelines to process
        discovered_values: Discovered property values
        lut_manager: LUT manager instance

    Returns:
        True if successful
    """
    print("\n" + "=" * 70)
    print("  Add LUTs by Rules - Console Mode")
    print("=" * 70)
    print("\nUIManager not available (Resolve Free or Studio not running)")
    print("Using console mode with predefined codec-to-LUT mappings")

    # Show discovered values
    print("\nDiscovered properties in project:")
    print(f"  Codecs: {', '.join(discovered_values.get('codecs', ['(none)']))}")
    print(f"  Resolutions: {', '.join(discovered_values.get('resolutions', ['(none)']))}")
    print(f"  Frame Rates: {', '.join(discovered_values.get('frame_rates', ['(none)']))}")
    print(f"  Clip Colors: {', '.join(discovered_values.get('clip_colors', ['(none)']))}")

    # Show available LUTs
    lut_names = lut_manager.get_lut_display_names()
    print(f"\nAvailable LUTs ({len(lut_names)}):")
    for idx, lut in enumerate(lut_names[:10], 1):  # Show first 10
        print(f"  {idx}. {lut}")
    if len(lut_names) > 10:
        print(f"  ... and {len(lut_names) - 10} more")

    print("\nTo use this script with full UI, please run DaVinci Resolve Studio")
    print("or edit this script to add predefined codec-to-LUT mappings.")

    return True


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main() -> bool:
    """Main function."""
    print("\n" + "=" * 70)
    print("  Add LUTs by Rules")
    print("=" * 70)

    # Connect to Resolve
    resolve = get_resolve()
    if not resolve:
        return False

    # Get project
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        print("ERROR: Could not access Project Manager")
        return False

    project = project_manager.GetCurrentProject()
    if not project:
        print("ERROR: No project is currently open")
        return False

    print(f"✓ Connected to project: {project.GetName()}")

    # Get media pool
    media_pool = project.GetMediaPool()
    if not media_pool:
        print("ERROR: Could not access Media Pool")
        return False

    # Get selected items from media pool
    print("\nGetting selected timelines from Media Pool...")
    selected_items = media_pool.GetSelectedClips()

    if not selected_items:
        print("ERROR: No items selected in Media Pool")
        print("       Please select timeline items in the Media Pool and try again")
        return False

    # Get timeline names from selected MediaPoolItems
    # MediaPoolItems that represent timelines need to be converted to Timeline objects
    timeline_names: list[str] = []
    non_timeline_items: list[str] = []

    for item in selected_items:
        try:
            # Check if item is a timeline by looking at its properties
            props = item.GetClipProperty()
            if props:
                # Check if Type indicates it's a timeline
                item_type = props.get("Type", "")
                if "Timeline" in str(item_type) or "Compound" in str(item_type):
                    timeline_names.append(item.GetName())
                else:
                    non_timeline_items.append(item.GetName())
            else:
                non_timeline_items.append(item.GetName())
        except Exception:
            non_timeline_items.append(item.GetName() if hasattr(item, 'GetName') else "Unknown")

    if non_timeline_items:
        print(f"ERROR: {len(non_timeline_items)} non-timeline item(s) selected:")
        for name in non_timeline_items[:5]:  # Show first 5
            print(f"  - {name}")
        if len(non_timeline_items) > 5:
            print(f"  ... and {len(non_timeline_items) - 5} more")
        print("\nPlease select only timeline items from the Media Pool")
        return False

    if not timeline_names:
        print("ERROR: No timeline items found in selection")
        print("       Please select timeline items (not clips) from the Media Pool")
        return False

    # Now get the actual Timeline objects from the project by matching names
    print(f"\nFound {len(timeline_names)} timeline name(s), getting Timeline objects...")
    timelines: list[Any] = []
    timeline_count = project.GetTimelineCount()

    for timeline_name in timeline_names:
        found = False
        for idx in range(1, timeline_count + 1):
            timeline = project.GetTimelineByIndex(idx)
            if timeline and timeline.GetName() == timeline_name:
                timelines.append(timeline)
                found = True
                break

        if not found:
            print(f"WARNING: Could not find timeline '{timeline_name}' in project")

    if not timelines:
        print("ERROR: Could not get Timeline objects from project")
        return False

    print(f"✓ Successfully got {len(timelines)} Timeline object(s):")
    for timeline in timelines:
        print(f"  - {timeline.GetName()}")

    # Scan selected timelines for property values
    print("\n" + "-" * 70)
    scanner = ProjectScanner(timelines)
    if not scanner.scan_timelines():
        print("ERROR: Failed to scan selected timelines")
        return False

    discovered_values = scanner.get_discovered_values()

    # Check if any properties were found
    if not any(discovered_values.values()):
        print("WARNING: No clip properties discovered in project")
        print("         Make sure your timelines contain clips with video")
        return False

    # Scan for available LUTs
    print("\n" + "-" * 70)
    print("Scanning for available LUTs...")
    lut_manager = LUTManager()
    lut_manager.scan_luts()
    lut_count = len(lut_manager.available_luts)
    print(f"✓ Found {lut_count} LUT file(s)")

    if lut_count == 0:
        print("WARNING: No LUTs found in standard folders")
        print("         You may need to add LUTs to DaVinci Resolve's LUT folder")

    # Try to create dialog (Studio version)
    print("\n" + "-" * 70)
    print("Opening dialog...")

    try:
        dialog = AddLUTDialog(resolve, timelines, discovered_values, lut_manager)
        dialog.create_dialog()
    except Exception as e:
        print(f"Could not create UI dialog: {e}")
        print("Falling back to console mode...")
        console_mode(resolve, timelines, discovered_values, lut_manager)

    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    success: bool = main()
    sys.exit(0 if success else 1)
