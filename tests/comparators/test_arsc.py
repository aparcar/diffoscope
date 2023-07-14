#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2023 FC Stegerman <flx@obfusk.net>
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

import pytest

from diffoscope.config import Config
from diffoscope.comparators.arsc import ArscFile
from diffoscope.comparators.missing_file import MissingFile

from ..utils.data import load_fixture, get_data
from ..utils.tools import skip_unless_tools_exist


arsc1 = load_fixture("resources1.arsc")
arsc2 = load_fixture("resources2.arsc")


def test_identification(arsc1):
    assert isinstance(arsc1, ArscFile)


def test_no_differences(arsc1):
    difference = arsc1.compare(arsc1)
    assert difference is None


@pytest.fixture
def differences(arsc1, arsc2):
    return arsc1.compare(arsc2).details


def check_arsc_differences(differences, expected_diff):
    assert differences[0].source1 == "aapt2 dump resources {}"
    assert differences[0].source2 == "aapt2 dump resources {}"
    assert expected_diff == differences[0].unified_diff


@skip_unless_tools_exist("aapt2")
@pytest.mark.xfail(strict=False)
def test_differences(differences):
    expected_diff = get_data("arsc_expected_diff")
    check_arsc_differences(differences, expected_diff)


@skip_unless_tools_exist("aapt2")
def test_compare_non_existing(monkeypatch, arsc1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = arsc1.compare(MissingFile("/nonexisting", arsc1))
    assert difference.source2 == "/nonexisting"
