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

import re
import subprocess

from diffoscope.difference import Difference
from diffoscope.exc import RequiredToolNotFound
from diffoscope.tools import tool_required

from .text import TextFile
from .utils.command import Command


class Htmltotext(Command):
    @tool_required("html2text")
    def cmdline(self):
        return ["html2text", self.path]


class HtmlFile(TextFile):
    DESCRIPTION = "HTML files (.html)"
    FILE_TYPE_RE = re.compile(r"^HTML document")

    def compare(self, other, source=None):
        difference = super().compare(other, source)

        if difference is None:
            return difference

        # Show text-only differences as a sub-diff.
        try:
            text = Difference.from_operation(Htmltotext, self.path, other.path)
            if text is not None:
                difference.add_details([text])
        except RequiredToolNotFound as exc:  # noqa
            difference.add_comment(exc.get_comment())
        except subprocess.CalledProcessError:
            pass

        return difference
