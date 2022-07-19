from typing import Any

import pytest
import requests
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from requests_mock import Mocker

from dhos_pdf_api import trustomer


@pytest.mark.usefixtures("app")
class TestTrustomer:
    def test_get_config_success(
        self, requests_mock: Mocker, trustomer_config: dict
    ) -> None:
        trustomer._cache.clear()
        mock_get: Any = requests_mock.get(
            f"{trustomer.get_trustomer_base_url()}/dhos/v1/trustomer/test",
            json=trustomer_config,
        )
        actual = trustomer.get_trustomer_config()
        assert actual == trustomer_config
        assert mock_get.call_count == 1
        assert (
            mock_get.last_request.headers["Authorization"]
            == "secret"  # From tox.ini env var
        )

    def test_get_config_failure(self, requests_mock: Mocker) -> None:
        trustomer._cache.clear()
        mock_get: Any = requests_mock.get(
            f"{trustomer.get_trustomer_base_url()}/dhos/v1/trustomer/test",
            exc=requests.exceptions.ConnectionError,
        )
        with pytest.raises(ServiceUnavailableException):
            trustomer.get_trustomer_config()
        assert mock_get.call_count == 1
