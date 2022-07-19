import json

import requests
from environs import Env

env = Env()
expected_trustomer = env.str("CUSTOMER_CODE").lower()
expected_product = "polaris"
expected_api_key = env.str("POLARIS_API_KEY")
trustomer_config = json.loads(env.str("MOCK_TRUSTOMER_CONFIG"))


def setup_mock_get_trustomer_config() -> None:
    payload = {
        "request": {
            "method": "GET",
            "url": "/dhos-trustomer/dhos/v1/trustomer/inttests",
            "headers": {
                "X-Trustomer": {"equalTo": expected_trustomer},
                "X-Product": {"equalTo": expected_product},
                "Authorization": {"equalTo": expected_api_key},
            },
        },
        "response": {"jsonBody": trustomer_config},
    }
    response = requests.post(f"http://wiremock:8080/__admin/mappings", json=payload)
    response.raise_for_status()
