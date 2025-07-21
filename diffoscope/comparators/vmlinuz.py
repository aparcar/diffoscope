#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2022, 2025 Chris Lamb <lamby@debian.org>
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

import logging
import pathlib
import re

from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command


logger = logging.getLogger(__name__)


class ExtractVmlinux(Command):
    def cmdline(self):
        # Locate extract-vmlinux script
        script = str(
            pathlib.Path(__file__).parent.parent.joinpath(
                "scripts", "extract-vmlinux"
            )
        )

        return [script, self.path]


class VmlinuzFile(File):
    DESCRIPTION = "Linux kernel images"
    FILE_TYPE_RE = re.compile(r"^Linux kernel\b")

    def compare_details(self, other, source=None):
        return [
            Difference.from_operation(ExtractVmlinux, self.path, other.path)
        ]
