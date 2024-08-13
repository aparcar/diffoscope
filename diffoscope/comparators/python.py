#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021-2022, 2024 Chris Lamb <lamby@debian.org>
# Copyright © 2021 Sergei Trofimovich
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

import binascii
import io
import os
import re
import struct
import time

from diffoscope.difference import Difference

from .missing_file import MissingFile
from .utils.file import File

re_memory_address = re.compile(r" at 0x\w+(?=, )")


class PycFile(File):
    DESCRIPTION = "Python .pyc files"
    FILE_TYPE_RE = re.compile(
        r"(^python .*byte-compiled$|^Byte-compiled Python module for CPython .*)"
    )
    FALLBACK_FILE_EXTENSION_SUFFIX = {".pyc"}

    def compare_details(self, other, source=None):
        if isinstance(other, MissingFile):
            return []

        try:
            return [
                Difference.from_text(
                    describe_pyc(self.path),
                    describe_pyc(other.path),
                    self.path,
                    other.path,
                    source="Python bytecode",
                )
            ]
        except (ValueError, IndexError, struct.error) as exc:
            self.add_comment("Could not decompile bytecode: {}".format(exc))
            return []


def describe_pyc(filename):
    with open(filename, "rb") as f:
        return "\n".join(parse_pyc(f))


def parse_pyc(f):
    f.seek(0, io.SEEK_END)
    if f.tell() == 0:
        yield "type:     empty"
        return

    f.seek(0)
    magic = f.read(4)
    yield "magic:    {}".format(hexlify(magic))

    f.seek(4, 1)
    moddate = f.read(4)
    modtime = time.asctime(time.gmtime(struct.unpack("<L", moddate)[0]))
    yield "moddate:  {} ({} UTC)".format(hexlify(moddate), modtime)

    filesz = f.read(4)
    filesz = struct.unpack("<L", filesz)
    yield f"files sz: {filesz[0]}"

    start = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell() - start
    yield f"code:     starts at offset {start} (size: {size} bytes)"


def hexlify(val):
    return "0x{}".format(binascii.hexlify(val).decode("utf-8"))
