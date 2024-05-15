#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2020, 2024 Chris Lamb <lamby@debian.org>
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

import re
import os.path
import logging
import subprocess

from diffoscope.tools import tool_required
from diffoscope.difference import Difference

from .utils.file import File
from .utils.archive import Archive
from .utils.command import Command

logger = logging.getLogger(__name__)


class XZList(Command):
    @tool_required("xz")
    def cmdline(self):
        return ("xz", "--list", "--verbose", "--verbose", self.path)

    def filter(self, line):
        # Strip the first line
        if line.startswith(self.path.encode("utf-8")):
            return b""
        return line


class XzContainer(Archive):
    def open_archive(self):
        return self

    def close_archive(self):
        pass

    def get_member_names(self):
        return [self.get_compressed_content_name(".xz")]

    @tool_required("xz")
    def extract(self, member_name, dest_dir):
        dest_path = os.path.join(dest_dir, member_name)
        logger.debug("xz extracting to %s", dest_path)
        with open(dest_path, "wb") as fp:
            subprocess.check_call(
                ["xz", "--decompress", "--stdout", self.source.path],
                stdout=fp,
                stderr=None,
            )
        return dest_path


class XzFile(File):
    DESCRIPTION = "XZ compressed files"
    CONTAINER_CLASSES = [XzContainer]
    FILE_TYPE_RE = re.compile(r"^XZ compressed data\b")

    # Work around file(1) Debian bug #876316
    FALLBACK_FILE_EXTENSION_SUFFIX = {".xz"}
    FALLBACK_FILE_TYPE_HEADER_PREFIX = b"\xfd7zXZ\x00"

    def compare(self, other, source=None):
        difference = super().compare(other, source)

        # Append xz --list *after* showing any container differences.
        if difference and not difference.details and isinstance(other, XzFile):
            xz_list = Difference.from_operation(
                XZList, self.path, other.path, source="xz --list"
            )
            if xz_list:
                difference.add_details([xz_list])

        return difference
