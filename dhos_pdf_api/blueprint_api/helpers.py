import os
import tempfile
from datetime import datetime
from typing import Any, Optional

import pytz
from flask import current_app
from flask_batteries_included.helpers.timestamp import (
    parse_iso8601_to_date,
    parse_iso8601_to_datetime,
)
from she_logging import logger

PDF_DATETIME_FORMAT = "%d-%b-%Y %H:%M:%S"
XML_DATE_FORMAT = "%Y%m%d"
XML_DATETIME_FORMAT = "%Y%m%d %H:%M:%S"


def yes_no_not_specified(value: Any) -> str:
    if value is True:
        return "YES"

    if value is False:
        return "NO"

    return "NOT SPECIFIED"


def format_iso8601_datestring_to_pdf_format(value: Any) -> str:

    if value and type(value) != str:
        return value.strftime(PDF_DATETIME_FORMAT)

    return value


def value_or_none(value: Any) -> str:
    if value is not None and value != "":
        return str(value)
    return "NOT SPECIFIED"


def write_file(file_destination: str, content: bytes) -> None:
    # Make dir if it doesn't already exist
    temp_dir: str = os.path.abspath(current_app.config["SEND_TMP_OUTPUT_DIR"])
    with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir) as fp:
        temp_filename: str = fp.name
        fp.write(content)
        fp.flush()
        os.fsync(fp.fileno())
    try:
        os.replace(temp_filename, file_destination)
    except OSError:
        logger.exception("Failed to move '%s' to '%s'", temp_filename, file_destination)


def xml_opt_datetime_convert(datetime_to_convert: Optional[str]) -> Optional[str]:
    if not datetime_to_convert:
        return None
    return xml_datetime_convert(datetime_to_convert)


def xml_datetime_convert(datetime_to_convert: str) -> str:
    if len(datetime_to_convert) == 10:
        date_obj = parse_iso8601_to_date(datetime_to_convert)
        assert date_obj is not None  # because mypy can't tell
        return date_obj.strftime(XML_DATE_FORMAT)

    datetime_obj = parse_iso8601_to_datetime(datetime_to_convert)
    assert datetime_obj is not None  # because mypy can't tell
    return datetime_obj.strftime(XML_DATETIME_FORMAT)


def get_datetime_now() -> datetime:
    return datetime.now(tz=pytz.utc)


def get_iso_format_time_now() -> str:
    return get_datetime_now().isoformat()
