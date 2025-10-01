#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2025 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import logging
import subprocess

from diffoscope.difference import Difference
from diffoscope.tempfiles import get_temporary_directory
from diffoscope.tools import tool_required

from .utils.archive import Archive, ArchiveMember
from .utils.command import Command
from .utils.file import File

logger = logging.getLogger(__name__)


def detect_apk_version(path):
    """Detect Alpine APK version by examining the file header."""
    try:
        with open(path, "rb") as f:
            header = f.read(16)
            if header.startswith(b"ADBd"):
                return 3
            elif header.startswith(b"\x1f\x8b"):  # gzip magic
                return 2
            else:
                return None
    except (IOError, OSError):
        return None


class AlpineApkV2Metadata(Command):
    """Extract metadata from Alpine APK v2 packages using tar extraction."""
    @tool_required("tar")
    def cmdline(self):
        # Extract control segment (second gzip stream) and show PKGINFO
        return ["sh", "-c", f"gunzip -c '{self.path}' | tar -xOf - ./PKGINFO 2>/dev/null || echo 'No PKGINFO found'"]


class AlpineApkV3Metadata(Command):
    """Extract metadata from Alpine APK v3 packages using apk adbdump."""
    @tool_required("apk")
    def cmdline(self):
        return ["apk", "adbdump", self.path]


class AlpineApkV2Container(Archive):
    """Container for Alpine APK v2 packages (gzipped tar segments)."""
    @property
    def path(self):
        return self._path

    @tool_required("tar")
    def open_archive(self):
        self._members = []
        self._tmpdir = get_temporary_directory(suffix="alpine-apk-v2")

        logger.debug(
            "Extracting APK v2 %s to %s", self.source.name, self._tmpdir.name
        )

        # APK v2 format: Extract the data segment (third gzip stream)
        # We use a shell command to skip the first two gzip streams
        cmd = [
            "sh", "-c",
            f"gunzip -c '{self.source.path}' | "
            f"gunzip -c | "
            f"tar -xf - -C '{self._tmpdir.name}' 2>/dev/null || "
            f"gunzip -c '{self.source.path}' | "
            f"tar -xf - -C '{self._tmpdir.name}'"
        ]
        
        try:
            subprocess.check_call(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.warning("Failed to extract APK v2 with complex method, trying simple extraction: %s", e)
            # Fallback: try simple tar extraction
            subprocess.check_call(
                ["tar", "-xzf", self.source.path, "-C", self._tmpdir.name],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

        # Collect all extracted files
        for root, dirs, files in os.walk(self._tmpdir.name):
            # Sort for reproducible output
            dirs.sort()
            files.sort()

            for filename in files:
                abspath = os.path.join(root, filename)
                relpath = abspath[len(self._tmpdir.name) + 1:]
                self._members.append(relpath)

        return self

    def close_archive(self):
        if hasattr(self, "_tmpdir"):
            self._tmpdir.cleanup()

    def get_member_names(self):
        return self._members

    def get_member(self, member_name):
        return ArchiveMember(self, member_name)

    def extract(self, member_name, dest_dir):
        return os.path.join(self._tmpdir.name, member_name)


class AlpineApkV3Container(Archive):
    """Container for Alpine APK v3 packages (ADBd format)."""
    @property
    def path(self):
        return self._path

    @tool_required("apk")
    def open_archive(self):
        self._members = []
        self._tmpdir = get_temporary_directory(suffix="alpine-apk-v3")

        logger.debug(
            "Extracting APK v3 %s to %s", self.source.name, self._tmpdir.name
        )

        # Extract package contents using apk --allow-untrusted extract
        subprocess.check_call(
            [
                "apk",
                "--allow-untrusted",
                "extract",
                "--destination",
                self._tmpdir.name,
                self.source.path,
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        # Collect all extracted files
        for root, dirs, files in os.walk(self._tmpdir.name):
            # Sort for reproducible output
            dirs.sort()
            files.sort()

            for filename in files:
                abspath = os.path.join(root, filename)
                relpath = abspath[len(self._tmpdir.name) + 1:]
                self._members.append(relpath)

        return self

    def close_archive(self):
        if hasattr(self, "_tmpdir"):
            self._tmpdir.cleanup()

    def get_member_names(self):
        return self._members

    def get_member(self, member_name):
        return ArchiveMember(self, member_name)

    def extract(self, member_name, dest_dir):
        return os.path.join(self._tmpdir.name, member_name)


class AlpineApkFile(File):
    DESCRIPTION = "Alpine APK packages"
    FILE_EXTENSION_SUFFIX = {".apk"}
    
    @classmethod
    def recognizes(cls, file):
        """Recognize both Alpine APK v2 and v3 formats."""
        if not file.name.endswith('.apk'):
            return False
        
        # Check file header to determine format
        try:
            with open(file.path, "rb") as f:
                header = f.read(16)
                # v3 format starts with "ADBd"
                if header.startswith(b"ADBd"):
                    return True
                # v2 format starts with gzip magic bytes
                if header.startswith(b"\x1f\x8b"):
                    return True
        except (IOError, OSError):
            pass
        
        return False

    @property
    def as_container(self):
        """Return appropriate container class based on APK version."""
        version = detect_apk_version(self.path)
        if version == 3:
            return AlpineApkV3Container(self)
        elif version == 2:
            return AlpineApkV2Container(self)
        return None

    def compare_details(self, other, source=None):
        differences = []

        # Detect versions of both files
        my_version = detect_apk_version(self.path)
        other_version = detect_apk_version(other.path)

        # Add version information as comment
        if my_version and other_version:
            if my_version != other_version:
                self.add_comment(f"APK version mismatch: {my_version} vs {other_version}")
            else:
                self.add_comment(f"Both files are APK v{my_version}")

        # Compare APK metadata using appropriate method
        try:
            if my_version == 3 and other_version == 3:
                # Both are v3, use apk adbdump
                metadata_diff = Difference.from_operation(
                    AlpineApkV3Metadata, self.path, other.path
                )
            elif my_version == 2 and other_version == 2:
                # Both are v2, extract PKGINFO from control segment
                metadata_diff = Difference.from_operation(
                    AlpineApkV2Metadata, self.path, other.path
                )
            else:
                # Mixed versions or unknown, try both methods
                try:
                    metadata_diff = Difference.from_operation(
                        AlpineApkV3Metadata, self.path, other.path
                    )
                except:
                    metadata_diff = Difference.from_operation(
                        AlpineApkV2Metadata, self.path, other.path
                    )
            
            if metadata_diff is not None:
                differences.append(metadata_diff)
                
        except Exception as exc:
            logger.debug("Failed to extract APK metadata: %s", exc)
            self.add_comment(f"APK metadata extraction failed: {exc}")

        return differences
