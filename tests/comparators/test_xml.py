#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright (C) 2017 Juliana Rodrigues <juliana.orod@gmail.com>
# Copyright © 2017, 2019-2020, 2022-2023, 2025 Chris Lamb <lamby@debian.org>
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

import sys
import pytest

from diffoscope.comparators.xml import XMLFile, is_vulnerable_xml_parser

from ..utils.data import load_fixture, assert_diff

skip_if_vulnerable_xml_parser = pytest.mark.skipif(
    is_vulnerable_xml_parser(), reason="Vulnerable XML parser"
)


xml_a = load_fixture("test1.xml")
xml_b = load_fixture("test2.xml")
xml_c = load_fixture("test3.xml")
xml_d = load_fixture("test4.xml")
invalid_xml = load_fixture("test_invalid.xml")


@skip_if_vulnerable_xml_parser
def test_identification(xml_a):
    assert isinstance(xml_a, XMLFile)


@skip_if_vulnerable_xml_parser
def test_invalid(invalid_xml):
    assert not isinstance(invalid_xml, XMLFile)


@skip_if_vulnerable_xml_parser
def test_no_differences(xml_a):
    assert xml_a.compare(xml_a) is None


@pytest.fixture
def differences(xml_a, xml_b):
    return xml_a.compare(xml_b).details


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires Python 3.8 or higher"
)
@skip_if_vulnerable_xml_parser
def test_diff(differences):
    assert_diff(differences[0], "test_xml_expected_diff")


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires Python 3.8 or higher"
)
@skip_if_vulnerable_xml_parser
def test_ordering_differences(xml_c, xml_d):
    diff = xml_c.compare(xml_d)
    assert diff.details[0].comments == ["Ordering differences only"]
    assert_diff(diff.details[0], "test_xml_ordering_differences_diff")
