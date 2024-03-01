#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2024 Chris Lamb <lamby@debian.org>
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

from diffoscope.comparators.gzip import GzipFile
from diffoscope.comparators.sevenz import SevenZFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist
from ..utils.nonexisting import assert_non_existing

sevenza = load_fixture("test1.disk.gz")
sevenzb = load_fixture("test2.disk.gz")


def test_identification(sevenza):
    assert isinstance(sevenza, GzipFile)


def test_no_differences(sevenza):
    difference = sevenza.compare(sevenza)
    assert difference is None


@pytest.fixture
def differences(sevenza, sevenzb):
    return sevenza.compare(sevenzb).details


@skip_unless_tools_exist("7z")
def test_content_source(differences):
    # We gzip our test data image, so we need to go one level deeper.
    assert differences[0].source1 == "test1.disk"
    assert differences[0].source2 == "test2.disk"
    assert differences[0].details[0].source1 == "7z l"
    assert differences[0].details[0].source2 == "7z l"


@skip_unless_tools_exist("7z")
def test_content_source_without_extension(tmpdir, sevenza, sevenzb):
    path1 = str(tmpdir.join("test1"))
    path2 = str(tmpdir.join("test2"))
    shutil.copy(sevenza.path, path1)
    shutil.copy(sevenzb.path, path2)
    sevenza = specialize(FilesystemFile(path1))
    sevenzb = specialize(FilesystemFile(path2))
    difference = sevenza.compare(sevenzb).details
    assert difference[0].source1 == "test1-content"
    assert difference[0].source2 == "test2-content"


@skip_unless_tools_exist("7z")
def test_metadata_diff(differences):
    assert_diff(differences[0].details[0], "text_sevenzmetadata_expected_diff")


@skip_unless_tools_exist("7z")
def test_compare_non_existing(monkeypatch, sevenza):
    assert_non_existing(monkeypatch, sevenza)
