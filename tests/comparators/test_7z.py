#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2023 Chris Lamb <lamby@debian.org>
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

from diffoscope.comparators.lz4 import Lz4File
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist
from ..utils.nonexisting import assert_non_existing

lz4a = load_fixture("test1.lz4")
lz4b = load_fixture("test2.lz4")


def test_identification(lz4a):
    assert isinstance(lz4a, Lz4File)


def test_no_differences(lz4a):
    difference = lz4a.compare(lz4a)
    assert difference is None


@pytest.fixture
def differences(lz4a, lz4b):
    return lz4a.compare(lz4b).details


@skip_unless_tools_exist("lz4")
def test_content_source(differences):
    assert differences[0].source1 == "test1"
    assert differences[0].source2 == "test2"


@skip_unless_tools_exist("lz4")
def test_content_source_without_extension(tmpdir, lz4a, lz4b):
    path1 = str(tmpdir.join("test1"))
    path2 = str(tmpdir.join("test2"))
    shutil.copy(lz4a.path, path1)
    shutil.copy(lz4b.path, path2)
    lz4a = specialize(FilesystemFile(path1))
    lz4b = specialize(FilesystemFile(path2))
    difference = lz4a.compare(lz4b).details
    assert difference[0].source1 == "test1-content"
    assert difference[0].source2 == "test2-content"


@skip_unless_tools_exist("lz4")
def test_content_diff(differences):
    assert_diff(differences[0], "text_ascii_expected_diff")


@skip_unless_tools_exist("lz4")
def test_compare_non_existing(monkeypatch, lz4a):
    assert_non_existing(monkeypatch, lz4a)
