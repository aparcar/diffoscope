#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2024 Jelle van der Waa <jelle@archlinux.org>
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


import subprocess
import re
import logging

from diffoscope.tools import tool_required, tool_check_installed
from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command, our_check_output

logger = logging.getLogger(__name__)


class UKIDump(Command):
    @tool_required("ukify")
    def cmdline(self):
        return ["ukify", "inspect", self.path]


class UKIFile(File):
    DESCRIPTION = "UKI image (.efi)"
    FILE_EXTENSION_SUFFIX = {".efi"}
    FILE_TYPE_RE = re.compile(r"^PE32\+")

    @classmethod
    def recognizes(cls, file):
        if not super().recognizes(file):
            return False

        if not tool_check_installed("objdump"):
            return False

        try:
            our_check_output(
                ["objdump", "-h", "--section", ".linux", file.path],
            )
            return True
        except subprocess.SubprocessError:
            return False

    def compare_details(self, other, source=None):
        return [Difference.from_operation(UKIDump, self.path, other.path)]
