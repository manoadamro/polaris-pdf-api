import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Generator
from uuid import uuid4

import kombu_batteries_included
import pytest
from _pytest.monkeypatch import MonkeyPatch
from flask import Flask
from lxml import etree
from mock import Mock
from pytest_mock import MockFixture
from she_logging.request_id import reset_request_id, set_request_id

from dhos_pdf_api import trustomer


@pytest.fixture
def app(pdf_output_path: str) -> Flask:
    """ "Fixture that creates app for testing"""
    from dhos_pdf_api.app import create_app

    current_app = create_app(testing=True, use_pgsql=False, use_sqlite=True)
    current_app.config["SEND_WARD_REPORT_OUTPUT_DIR"] = str(pdf_output_path)

    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xsd = os.path.join(
        root_path, "dhos_pdf_api", "schema", "infrastructure", "cda", "CDA_SDTC.xsd"
    )
    with open(xsd, "r") as f:
        schema_doc = etree.parse(f)
        schema = etree.XMLSchema(schema_doc)
        current_app.config["CDA_XML_SCHEMA_PARSER"] = etree.XMLParser(schema=schema)
    return current_app


@pytest.fixture
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture()
def mock_bearer_validation(mocker: MockFixture) -> Any:
    from jose import jwt

    mocked = mocker.patch.object(jwt, "get_unverified_claims")
    mocked.return_value = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1_516_239_022,
        "iss": "http://localhost/",
    }
    return mocked


@pytest.fixture
def pdf_output_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    pdf_output_path = tmp_path / "send_ward_report"
    pdf_output_path.mkdir()
    monkeypatch.setenv("SEND_WARD_REPORT_OUTPUT_DIR", str(pdf_output_path))
    return pdf_output_path


@pytest.fixture
def sample_gdm_data() -> Dict:
    """Sample data used to generate GDM PDF"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "gdm_pdf.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture
def sample_gdm_data_handled() -> Dict:
    """Sample data handled by the schema"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "gdm_pdf_handled.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture(scope="session")
def sample_send_data_session() -> Dict:
    """Sample data used to generate SEND PDF"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "send_pdf.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture(scope="session")
def sample_send_data_schema_session() -> Dict:
    """Sample processed data used to generate SEND PDF"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "send_pdf_schema.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture
def date_of_birth() -> str:
    return "1985-07-01"


@pytest.fixture
def sample_send_data(sample_send_data_session: Dict, date_of_birth: str) -> Dict:
    data = deepcopy(sample_send_data_session)
    data["patient"]["dob"] = date_of_birth
    return data


@pytest.fixture
def trustomer_config() -> Dict:
    """Trustomer configuration"""
    return {
        "send_config": {
            "news2": {
                "zero_severity_interval_hours": 12,
                "low_severity_interval_hours": 4,
                "low_medium_severity_interval_hours": 1,
                "medium_severity_interval_hours": 1,
                "high_severity_interval_hours": 0,
                "escalation_policy": {
                    "routine_monitoring": "<p>Continue routine NEWS monitoring</p>",
                    "low_monitoring": "<p>Inform registered nurse, who must assess the patient</p><p>Registered nurse decides whether increased frequency of monitoring and/or escalation of care is required</p>",
                    "low_medium_monitoring": "<p>Registered nurse to inform medical team caring for the patient, who will review and decide whether escalation of care is necessary</p>",
                    "medium_monitoring": "<p>Registered nurse to immediately inform the medical team caring for the patient</p><p>Registered nurse to request urgent assessment by a clinician or team with core competencies in the care of acutely ill patients</p><p>Provide clinical care in an environment with monitoring facilities</p>",
                    "high_monitoring": "<p>Registered nurse to immediately inform the medical team caring for the patient – this should be at least at specialist registrar level</p><p>Emergency assessment by a team with critical care competencies, including practitioner(s) with advanced airway management skills</p><p>Consider transfer of care to a level 2 or 3 clinical care facility, ie higher-dependency unit or ICU</p><p>Clinical care in an environment with monitoring facilities</p>",
                },
            },
            "oxygen_masks": [
                {"code": "RA", "name": "Room Air"},
                {"code": "V{mask_percent}", "name": "Venturi"},
                {"code": "H{mask_percent}", "name": "Humidified"},
                {"code": "HIF{mask_percent}", "name": "High Flow"},
                {"code": "N", "name": "Nasal cann."},
                {"code": "SM", "name": "Simple"},
                {"code": "RM", "name": "Resv mask"},
                {"code": "TM", "name": "Trach."},
                {"code": "CP", "name": "CPAP"},
                {"code": "NIV", "name": "NIV"},
                {"code": "OPT", "name": "Optiflow"},
                {"code": "NM", "name": "Nebuliser"},
            ],
        }
    }


@pytest.fixture
def test_request_id() -> Generator[str, None, None]:
    request_id = str(uuid4())
    token = set_request_id(request_id)
    yield request_id
    reset_request_id(token)


@pytest.fixture
def mock_trustomer_config(mocker: MockFixture, trustomer_config: Dict) -> Mock:
    """Mock trustomer config get"""
    return mocker.patch.object(
        trustomer, "get_trustomer_config", return_value=trustomer_config
    )


@pytest.fixture
def mock_publish_msg(mocker: MockFixture) -> Mock:
    return mocker.patch.object(kombu_batteries_included, "publish_message")


@pytest.fixture(scope="session")
def sample_send_post_data_session() -> Dict:
    """Sample data used to generate SEND PDF"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "send_pdf_post.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture(scope="session")
def sample_send_cda_post_data_session() -> Dict:
    """Sample data used to generate SEND CDA"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "send_pdf_cda_post.json")
    with open(filename, "r") as f:
        return json.loads(f.read())


@pytest.fixture(scope="session")
def sample_dbm_post_data_session() -> Dict:
    """Sample data used to generate DBM PDF"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root_path, "sample_data", "dbm_pdf_post.json")
    with open(filename, "r") as f:
        return json.loads(f.read())
