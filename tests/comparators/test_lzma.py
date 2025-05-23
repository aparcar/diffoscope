#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2016-2017, 2020, 2024-2025 Chris Lamb <lamby@debian.org>
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

import shutil
import pytest

from diffoscope.comparators.lzma import LzmaFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist
from ..utils.nonexisting import assert_non_existing

lzma1 = load_fixture("test1.lzma")
lzma2 = load_fixture("test2.lzma")


def test_identification(lzma1):
    assert isinstance(lzma1, LzmaFile)


def test_no_differences(lzma1):
    difference = lzma1.compare(lzma1)
    assert difference is None


@pytest.fixture
def differences(lzma1, lzma2):
    return lzma1.compare(lzma2).details


@skip_unless_tools_exist("xz")
def test_content_source(differences):
    assert differences[0].source1 == "test1"
    assert differences[0].source2 == "test2"


@skip_unless_tools_exist("xz")
def test_content_source_without_extension(tmpdir, lzma1, lzma2):
    path1 = str(tmpdir.join("test1"))
    path2 = str(tmpdir.join("test2"))
    shutil.copy(lzma1.path, path1)
    shutil.copy(lzma2.path, path2)
    lzma1 = specialize(FilesystemFile(path1))
    lzma2 = specialize(FilesystemFile(path2))
    difference = lzma1.compare(lzma2).details
    assert difference[0].source1 == "test1-content"
    assert difference[0].source2 == "test2-content"


@skip_unless_tools_exist("xz")
def test_content_diff(differences):
    assert_diff(differences[0], "text_ascii_expected_diff")


@skip_unless_tools_exist("xz")
def test_compare_non_existing(monkeypatch, lzma1):
    assert_non_existing(monkeypatch, lzma1)
