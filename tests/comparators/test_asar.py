#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2017, 2020 Chris Lamb <lamby@debian.org>
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

import pytest

from diffoscope.config import Config
from diffoscope.comparators.asar import AsarFile
from diffoscope.comparators.missing_file import MissingFile

from ..utils.data import load_fixture, get_data
from ..utils.tools import skip_unless_tools_exist
from ..utils.nonexisting import assert_non_existing


asar1 = load_fixture("test1.asar")
asar2 = load_fixture("test2.asar")


def test_identification(asar1):
    assert isinstance(asar1, AsarFile)


def test_no_differences(asar1):
    difference = asar1.compare(asar1)
    assert difference is None


@pytest.fixture
def differences(asar1, asar2):
    return asar1.compare(asar2).details


@skip_unless_tools_exist("asar")
def test_text_file(differences):
    assert differences[0].source1 == "dir/text"
    assert differences[0].source2 == "dir/text"
    expected_diff = get_data("text_ascii_expected_diff")
    assert differences[0].unified_diff == expected_diff
