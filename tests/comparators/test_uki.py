#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2024 Jelle van der Waa <jelle@archlinux.org>
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

from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.uki import UKIFile
from diffoscope.comparators.utils.command import our_check_output
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import assert_diff, load_fixture
from ..utils.tools import skip_unless_tools_exist

efi_stub = load_fixture("dummyx64.efi.stub")


def uki_fixture(prefix, os_release, uname):
    @pytest.fixture
    def uki(tmpdir, efi_stub):
        input_ = str(tmpdir.join(prefix))
        output = str(tmpdir.join("{}.unsigned.efi".format(prefix)))

        with open(input_, "w") as fp:
            fp.write("kernel")

        our_check_output(
            [
                "ukify",
                "build",
                "--stub",
                efi_stub.path,
                "--linux",
                input_,
                "--os-release",
                os_release,
                "--uname",
                uname,
            ],
            cwd=tmpdir,
        )

        return specialize(FilesystemFile(output))

    return uki


uki1 = uki_fixture("linux1", "arch", "6.11")
uki2 = uki_fixture("linux2", "debian", "6.12")


@pytest.fixture
def differences(uki1, uki2):
    return uki1.compare(uki2).details


@skip_unless_tools_exist("objdump")
@skip_unless_tools_exist("ukify")
def test_no_differences(uki1):
    difference = uki1.compare(uki1)
    assert difference is None


@skip_unless_tools_exist("objdump")
@skip_unless_tools_exist("ukify")
def test_diff(differences):
    assert_diff(differences[0], "uki_expected_diff")
