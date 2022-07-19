from typing import Dict

import pytest
from environs import Env
from flask_batteries_included.helpers import generate_uuid
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from mock import Mock
from pytest_mock import MockFixture
from textract import process
from werkzeug import Client

from dhos_pdf_api.blueprint_api import controller


@pytest.mark.usefixtures("mock_bearer_validation")
class TestApi:
    def test_create_gdm_patient_pdf_success(
        self,
        client: Client,
        mocker: MockFixture,
        sample_gdm_data: Dict,
        sample_gdm_data_handled: Dict,
    ) -> None:
        mock_create: Mock = mocker.patch.object(controller, "create_patient_pdf")
        response = client.post(
            "/dhos/v1/gdm_pdf",
            json=sample_gdm_data,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 201
        mock_create.assert_called_with(data=sample_gdm_data_handled, product_name="gdm")

    def test_create_gdm_patient_pdf_no_nhs_number(
        self,
        client: Client,
        mocker: MockFixture,
        sample_gdm_data: Dict,
        sample_gdm_data_handled: Dict,
    ) -> None:
        del sample_gdm_data["patient"]["nhs_number"]
        del sample_gdm_data_handled["patient"]["nhs_number"]
        mock_create: Mock = mocker.patch.object(controller, "create_patient_pdf")
        response = client.post(
            "/dhos/v1/gdm_pdf",
            json=sample_gdm_data,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 201
        mock_create.assert_called_with(data=sample_gdm_data_handled, product_name="gdm")

    def test_create_gdm_patient_pdf_bad_medication(
        self,
        client: Client,
        mocker: MockFixture,
        sample_gdm_data: Dict,
    ) -> None:
        env = Env()
        blood_glucose_readings = [
            {
                "blood_glucose_value": 7.2,
                "created": "2020-10-15T01:36:10.191Z",
                "created_by": "static_patient_uuid_2",
                "doses": [
                    {
                        "amount": 12.0,
                        "created": "2020-10-15T01:36:10.200Z",
                        "created_by": "static_patient_uuid_2",
                        "medication_id": "FAKE_ID",
                        "modified": "2020-10-15T01:36:10.200Z",
                        "modified_by": "static_patient_uuid_2",
                        "uuid": "d805a096-40ae-4492-9c23-d5af57337f7d",
                    }
                ],
                "measured_timestamp": "2020-10-14T20:16:48.685Z",
                "modified": "2020-10-15T01:36:10.679Z",
                "modified_by": "dhos-async-adapter",
                "patient_id": "static_patient_uuid_2",
                "prandial_tag": {
                    "created": "2020-01-21T17:03:23.182Z",
                    "created_by": "sys",
                    "description": "before_dinner",
                    "modified": "2020-01-21T17:03:23.182Z",
                    "modified_by": "sys",
                    "uuid": "PRANDIAL-TAG-BEFORE-DINNER",
                    "value": 5,
                },
                "reading_banding": {
                    "created": "2020-01-21T17:03:23.181Z",
                    "created_by": "sys",
                    "description": "high",
                    "modified": "2020-01-21T17:03:23.181Z",
                    "modified_by": "sys",
                    "uuid": "BG-READING-BANDING-HIGH",
                    "value": 3,
                },
                "reading_metadata": {},
                "units": "mmol/L",
                "uuid": "2282a04e-5e91-4911-bd17-41b37065d24f",
            }
        ]
        sample_gdm_data["blood_glucose_readings"] = blood_glucose_readings

        response = client.post(
            "/dhos/v1/gdm_pdf",
            json=sample_gdm_data,
            headers={"Authorization": "Bearer TOKEN"},
        )
        GDM_BCP_OUTPUT_DIR = env.str("GDM_BCP_OUTPUT_DIR")
        text = process(GDM_BCP_OUTPUT_DIR + "/Grace-Galloway-846-745-6483.pdf")

        assert response.status_code == 201
        assert b"UNKNOWN MEDICATION" in text
        assert b"1.5 units Humulin M3" in text
        assert b"Testing second message" in text

    def test_create_patient_pdf_no_body(self, client: Client) -> None:
        response = client.post(
            "/dhos/v1/gdm_pdf", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response
        assert response.status_code == 400
        assert response.json is not None
        assert response.json["detail"] == "None is not of type 'object'"

    def test_create_patient_pdf_wrong_method(self, client: Client) -> None:
        response = client.get(
            "/dhos/v1/gdm_pdf", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response
        assert response.status_code == 405

    def test_get_patient_pdf_success(self, client: Client, mocker: MockFixture) -> None:
        expected_response_data = b"1" * 100_000
        patient_uuid = generate_uuid()
        mock_get: Mock = mocker.patch.object(
            controller, "get_patient_pdf", return_value=expected_response_data
        )
        response = client.get(
            f"/dhos/v1/gdm_pdf/{patient_uuid}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        mock_get.assert_called_with(patient_uuid=patient_uuid, product_name="gdm")
        assert response.headers["Content-Type"] == "application/pdf"
        assert response.data == expected_response_data

    def test_aggregate_send_data_success(
        self,
        client: Client,
        mocker: MockFixture,
        sample_send_data_session: Dict,
        trustomer_config: Dict,
        sample_send_data_schema_session: Dict,
    ) -> None:
        mock_send = mocker.patch.object(controller, "create_send_documents")
        sample_send_data_session["trustomer"] = trustomer_config
        response = client.post(
            "/dhos/v1/send_pdf",
            json=sample_send_data_session,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 201
        mock_send.assert_called_with(sample_send_data_schema_session)

    def test_aggregate_send_data_no_body(self, client: Client) -> None:
        response = client.post(
            "/dhos/v1/send_pdf", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response
        assert response.status_code == 400
        assert response.json is not None
        assert response.json["detail"] == "None is not of type 'object'"

    def test_aggregate_send_data_error(
        self,
        client: Client,
        mocker: MockFixture,
        sample_send_data_session: Dict,
        trustomer_config: Dict,
    ) -> None:
        mock_create = mocker.patch.object(controller, "create_send_documents")
        mock_create.side_effect = ServiceUnavailableException()
        sample_send_data_session["trustomer"] = trustomer_config
        response = client.post(
            "/dhos/v1/send_pdf",
            json=sample_send_data_session,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response
        assert response.status_code == 503
        assert response.json is not None
        assert response.json["message"] == "Service unavailable"

    def test_send_pdf_post_success(
        self,
        client: Client,
        sample_send_post_data_session: Dict,
        mocker: MockFixture,
    ) -> None:
        mocker.patch.object(controller, "create_send_documents")
        response = client.post(
            "/dhos/v1/send_pdf",
            headers={"Authorization": "Bearer TOKEN"},
            json=sample_send_post_data_session,
        )
        assert response
        assert response.status_code == 201

    def test_send_pdf_post_cda_success(
        self,
        client: Client,
        sample_send_cda_post_data_session: Dict,
        mocker: MockFixture,
    ) -> None:
        mocker.patch.object(controller, "generate_send_pdf")
        mocker.patch.object(controller, "trustomer")
        mocker.patch.object(controller, "_save_filename_lookup")
        mocker.patch.object(controller, "write_file")

        response = client.post(
            "/dhos/v1/send_pdf",
            headers={"Authorization": "Bearer TOKEN"},
            json=sample_send_cda_post_data_session,
        )
        assert response
        assert response.status_code == 201

    def test_dbm_pdf_post_success(
        self,
        client: Client,
        sample_dbm_post_data_session: Dict,
        mocker: MockFixture,
    ) -> None:
        mocker.patch.object(controller, "create_patient_pdf")
        response = client.post(
            "/dhos/v1/dbm_pdf",
            headers={"Authorization": "Bearer TOKEN"},
            json=sample_dbm_post_data_session,
        )
        assert response
        assert response.status_code == 201
