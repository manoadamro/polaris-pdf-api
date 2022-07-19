from behave import step
from behave.runner import Context
from clients import wiremock_client


@step("the Trustomer API is running")
def setup_mock_trustomer_api(context: Context) -> None:
    wiremock_client.setup_mock_get_trustomer_config()
