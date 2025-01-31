#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
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

from diffoscope.tools import tool_required
from diffoscope.tempfiles import get_temporary_directory

from .utils.file import File
from .utils.archive import Archive
from .utils.command import our_check_output

logger = logging.getLogger(__name__)


class AsarContainer(Archive):
    @tool_required("asar")
    def open_archive(self):
        # Just extract the asar as a whole due to the problems mentioned below
        self._members = []
        self._unpacked = get_temporary_directory(suffix="asar")

        logger.debug("Extracting asar to %s", self._unpacked.name)

        our_check_output(
            [
                "asar",
                "extract",
                os.path.abspath(self.source.path),
                self._unpacked.name,
            ],
            cwd=self._unpacked.name,
        )

        for root, _, files in os.walk(self._unpacked.name):
            current_dir = []

            for filename in sorted(files):
                abspath = os.path.join(root, filename)

                relpath = abspath[len(self._unpacked.name) + 1 :]

                current_dir.append(relpath)

            self._members.extend(current_dir)

        return self

    def close_archive(self):
        self._unpacked.cleanup()

    def get_member_names(self):
        # 'asar list' returns all entries including directories, so it's hard to use
        # rely on extraction to temp directory instead
        return self._members

    def extract(self, member_name, dest_dir):
        # while 'asar' lets us extract single files, it does not let us specify where to output them at all.
        # rely on extraction to temp directory instead
        return os.path.join(self._unpacked.name, member_name)


class AsarFile(File):
    DESCRIPTION = "asar archives"
    CONTAINER_CLASSES = [AsarContainer]
    FILE_TYPE_RE = re.compile(r"^\bElectron ASAR archive\b")
