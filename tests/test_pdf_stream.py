from pathlib import Path
from typing import Any

import pytest
from flask_batteries_included.sqldb import db
from werkzeug import Client

from dhos_pdf_api.models.filename_lookup import FilenameLookup


@pytest.mark.usefixtures("app")
class TestPDFStream:
    def test_stream_response(
        self, client: Client, mocker: Any, mock_bearer_validation: Any
    ) -> None:
        mocker.patch.object(
            Path,
            "read_bytes",
            return_value=b"1" * 100_000,
        )
        first = FilenameLookup(
            uuid="some-uuid", file_name="some.pdf", lookup_uuid="1234"
        )
        db.session.add(first)
        db.session.commit()

        response = client.get(
            "dhos/v1/patient/pdf/1234", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 200
