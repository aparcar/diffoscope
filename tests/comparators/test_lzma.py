#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2025 Will Hollywood <will.d.hollywood@gmail.com>
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

from diffoscope.config import Config
from diffoscope.comparators.lzma import LzmaFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.missing_file import MissingFile
from diffoscope.comparators.utils.specialize import (
    specialize,
    is_direct_instance,
)

from ..utils.data import load_fixture, get_data


lzma1 = load_fixture("test1.lzma")
lzma2 = load_fixture("test2.lzma")


def test_identification(lzma1):
    assert is_direct_instance(lzma1, LzmaFile)


def test_no_differences(lzma1):
    difference = lzma1.compare(lzma1)
    assert difference is None


@pytest.fixture
def differences(lzma1, lzma2):
    return lzma1.compare(lzma2).details


def test_content_source(differences):
    assert differences[0].source1 == "test1"
    assert differences[0].source2 == "test2"


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


def test_content_diff(differences):
    expected_diff = get_data("text_ascii_expected_diff")
    assert differences[0].unified_diff == expected_diff


def test_compare_non_existing(monkeypatch, lzma1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = lzma1.compare(MissingFile("/nonexisting", lzma1))
    assert difference.source2 == "/nonexisting"
    assert difference.details[-1].source2 == "/dev/null"
