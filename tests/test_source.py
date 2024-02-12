#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2018-2024 Chris Lamb <lamby@debian.org>
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

import subprocess

from .utils.tools import skip_unless_tool_is_at_least


def black_version():
    try:
        out = subprocess.check_output(("black", "--version"))
    except subprocess.CalledProcessError as exc:
        out = exc.output

    # black --version format changed starting in 21.11b0. Returning the first
    # token starting with a decimal digit, since its ordinal position may vary.
    return [
        x for x in out.strip().decode("utf-8").split(" ") if x[0].isdigit()
    ]


@skip_unless_tool_is_at_least("black", black_version, "24.1.1")
def test_code_is_black_clean():
    output = subprocess.check_output(
        ("black", "--diff", "."), stderr=subprocess.PIPE
    ).decode("utf-8")

    # Display diff in "captured stdout call"
    if output:
        print(output)

    assert not output, output
