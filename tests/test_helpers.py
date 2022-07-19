import datetime
import filecmp
import os
import tempfile

import pytest

from dhos_pdf_api.blueprint_api import helpers


@pytest.mark.usefixtures("app")
class TestHelpers:
    def test_write_file(self) -> None:
        input_file = os.path.realpath(__file__)
        fh = open(input_file, "rb")
        fh.seek(0)
        content = fh.read()
        outfile = tempfile.NamedTemporaryFile(delete=False)
        outfile.close()
        helpers.write_file(outfile.name, content)
        assert filecmp.cmp(input_file, outfile.name)

    def test_yes_no_not_specified(self) -> None:
        assert helpers.yes_no_not_specified(True) == "YES"
        assert helpers.yes_no_not_specified(False) == "NO"
        assert helpers.yes_no_not_specified(None) == "NOT SPECIFIED"
        assert helpers.yes_no_not_specified(123) == "NOT SPECIFIED"

    def test_value_or_none(self) -> None:
        assert helpers.value_or_none(None) == "NOT SPECIFIED"
        assert helpers.value_or_none("") == "NOT SPECIFIED"
        assert helpers.value_or_none(123) == "123"
        assert helpers.value_or_none("yes") == "yes"

    def test_format_iso8601_datestring_to_pdf_format(self) -> None:
        dt = datetime.datetime(
            year=1970, month=12, day=15, hour=12, minute=23, second=44, microsecond=321
        )
        assert (
            helpers.format_iso8601_datestring_to_pdf_format(dt)
            == "15-Dec-1970 12:23:44"
        )
