#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2016, 2018-2024 Chris Lamb <lamby@debian.org>
# Copyright © 2023 Mattia Rizzolo <mattia@debian.org>
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
import os
import re

from diffoscope.tools import (
    python_module_missing,
    tool_required,
    get_package_provider,
)
from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command

logger = logging.getLogger(__name__)

PYPDF_MAJOR_VERSION = None

try:
    try:
        # PyPDF 3.x
        import pypdf
    except ImportError:
        # PyPDF2 1.x-2.x
        import PyPDF2 as pypdf

    try:
        try:
            # pyPDF 3.x
            from pypdf import PdfReader

            PYPDF_MAJOR_VERSION = 3
        except ImportError:
            # pyPDF 2.x
            import pypdf.PdfReader as PdfReader

            PYPDF_MAJOR_VERSION = 2
    except ImportError:
        # PyPDF2 1.x
        import pypdf.PdfFileReader as PdfReader

        PYPDF_MAJOR_VERSION = 1

    try:
        # PyPDF 3.x
        from pypdf.errors import PdfReadError
    except ImportError:
        try:
            # PyPDF 2.x
            from PyPDF2.errors import PdfReadError
        except ImportError:
            # PyPDF 1.x
            from PyPDF2.utils import PdfReadError

except (ImportError, RuntimeError):  # noqa
    python_module_missing("pypdf")
    pypdf = None


class Pdftotext(Command):
    @tool_required("pdftotext")
    def cmdline(self):
        return ["pdftotext", self.path, "-"]


class Dumppdf(Command):
    @tool_required("dumppdf")
    def cmdline(self):
        return ["dumppdf", "-at", self.path]


class PdfFile(File):
    DESCRIPTION = "PDF documents"
    FILE_TYPE_RE = re.compile(r"^PDF document\b")

    def compare_details(self, other, source=None):
        xs = []

        xs.append(Difference.from_operation(Pdftotext, self.path, other.path))

        # Include verbose dumppdf output unless we won't see any differences
        # without it.
        if not any(xs):
            xs.append(
                Difference.from_operation(Dumppdf, self.path, other.path)
            )

        # Always preppend metadata differences
        xs[:0] = self.gen_metadata_differences(other)

        return xs

    def gen_metadata_differences(self, other):
        if PYPDF_MAJOR_VERSION is None:
            pkg = get_package_provider("pypdf")
            infix = f" from the '{pkg}' package " if pkg else " "
            self.add_comment(
                f"Installing the 'pypdf' Python module{infix}"
                "may produce a better output."
            )

            return

        difference = Difference.from_text(
            self.dump_pypdf_metadata(self),
            self.dump_pypdf_metadata(other),
            self.name,
            other.name,
        )
        if difference:
            difference.add_comment("Document info")
        yield difference

        difference = Difference.from_text(
            self.dump_pypdf_annotations(self),
            self.dump_pypdf_annotations(other),
            self.name,
            other.name,
        )
        if difference:
            difference.add_comment("Annotations")
        yield difference

    def dump_pypdf_metadata(self, file):
        try:
            pdf = PdfReader(file.path)
            document_info = pdf.metadata

            if document_info is None:
                return ""

            xs = []
            for k, v in sorted(document_info.items()):
                xs.append("{}: {!r}".format(k.lstrip("/"), v))

            return "\n".join(xs)
        except PdfReadError as e:
            msg = "Could not extract pypdf metadata from {}: {}".format(
                os.path.basename(file.name), e
            )
            self.add_comment(msg)
            logger.error(msg)
            return ""

    def dump_pypdf_annotations(self, file):
        try:
            pdf = PdfReader(file.path)

            xs = []
            for x in range(len(pdf.pages)):
                page = pdf.pages[x]

                try:
                    for annot in page["/Annots"]:
                        if PYPDF_MAJOR_VERSION == 3:
                            subtype = annot.get_object()["/Subtype"]
                            if subtype == "/Text":
                                xs.append(annot.get_object()["/Contents"])
                        else:
                            subtype = annot.getObject()["/Subtype"]
                            if subtype == "/Text":
                                xs.append(annot.getObject()["/Contents"])
                except KeyError:
                    pass

            return "\n".join(xs)
        except PdfReadError as e:
            msg = "Could not extract pypdf annotations from {}: {}".format(
                os.path.basename(file.name), e
            )
            file.add_comment(msg)
            logger.error(msg)
            return ""
