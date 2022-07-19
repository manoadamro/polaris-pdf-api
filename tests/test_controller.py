import copy
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import requests
from _pytest.logging import LogCaptureFixture
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from flask_batteries_included.sqldb import db, generate_uuid
from mock import Mock
from pytest_mock import MockFixture
from requests_mock import Mocker

from dhos_pdf_api.blueprint_api import controller
from dhos_pdf_api.models.filename_lookup import FilenameLookup


@pytest.mark.usefixtures("app", "mock_trustomer_config")
class TestController:
    def test_create_gdm_patient_pdf(
        self, mocker: MockFixture, sample_gdm_data: Dict
    ) -> None:
        # Arrange
        expected = "something"
        patient_uuid: str = sample_gdm_data["patient"]["uuid"]
        first_name: str = sample_gdm_data["patient"]["first_name"]
        last_name: str = sample_gdm_data["patient"]["last_name"]
        nhs_number: str = sample_gdm_data["patient"]["nhs_number"]
        mock_pdfkit: Mock = mocker.patch("pdfkit.from_string", return_value=expected)
        mock_write = mocker.patch.object(Path, "write_bytes")
        mocker.patch.object(Path, "mkdir")

        # Act
        controller.create_patient_pdf(data=sample_gdm_data, product_name="gdm")

        # Assert
        assert mock_pdfkit.call_count == 1
        assert mock_write.call_count == 1
        mock_write.assert_called_with(expected)
        lookup = FilenameLookup.query.filter_by(lookup_uuid=patient_uuid).first()
        assert lookup is not None
        assert lookup.lookup_uuid == patient_uuid
        assert lookup.file_name == f"{first_name}-{last_name}-{nhs_number}.pdf"

    @pytest.mark.parametrize(
        "first_name,pdf_filename",
        [
            ("/etc?%+\\", "%2Fetc%3F%25%2B%5C-Galloway-846-745-6483.pdf"),  #
            ("/etc /", "%2Fetc+%2F-Galloway-846-745-6483.pdf"),
            ("etc/", "etc%2F-Galloway-846-745-6483.pdf"),
        ],
    )
    def test_create_gdm_patient_pdf_bad_file_name(
        self,
        mocker: MockFixture,
        sample_gdm_data: Dict,
        first_name: str,
        pdf_filename: str,
    ) -> None:
        # Arrange
        sample_gdm_data["patient"]["first_name"] = first_name
        patient_uuid: str = sample_gdm_data["patient"]["uuid"]
        mocker.patch("pdfkit.from_string", return_value={"some": "thing"})
        mocker.patch.object(Path, "write_bytes")
        mocker.patch.object(Path, "mkdir")

        controller.create_patient_pdf(data=sample_gdm_data, product_name="gdm")
        lookup = FilenameLookup.query.filter_by(lookup_uuid=patient_uuid).first()
        # Assert
        assert lookup.file_name == pdf_filename

    @pytest.mark.parametrize("product_name", ["gdm", "dbm"])
    def test_get_patient_pdf(
        self, mocker: MockFixture, sample_gdm_data: Dict, product_name: str
    ) -> None:
        # Arrange
        patient_uuid = sample_gdm_data["patient"]["uuid"]
        expected_path = "some.pdf"
        pdf_bytes = b"1" * 10
        first = FilenameLookup(
            uuid=generate_uuid(), file_name=expected_path, lookup_uuid=patient_uuid
        )
        db.session.add(first)
        db.session.commit()
        mock_read: Mock = mocker.patch.object(
            Path,
            "read_bytes",
            return_value=pdf_bytes,
        )

        # Act
        content = controller.get_patient_pdf(patient_uuid, product_name)

        # Assert
        assert mock_read.call_count == 1
        assert content == pdf_bytes

    def test_create_send_documents_success(
        self,
        sample_send_data: Dict,
        requests_mock: Mocker,
        mocker: MockFixture,
        test_request_id: str,
    ) -> None:
        mrn = sample_send_data["patient"]["hospital_number"]
        epr_encounter_id = sample_send_data["encounter"]["epr_encounter_id"]

        mock_post: Any = requests_mock.post(
            f"http://localhost:3000/dhos/v1/send_pdf",
            headers={"Content-Type": "application/pdf"},
            content=b"something",
            status_code=200,
        )

        mock_write = mocker.patch.object(controller, "write_file")
        mocker.patch("os.path.isdir", return_value=False)
        mocker.patch("os.mkdir")

        controller.create_send_documents(sample_send_data)
        assert mock_post.call_count == 1
        assert mock_post.last_request.json() == sample_send_data
        assert mock_post.last_request.headers["X-Request-ID"] == test_request_id

        encounter_uuid = sample_send_data["encounter"]["uuid"]
        lookup = FilenameLookup.query.filter_by(lookup_uuid=encounter_uuid).first()
        assert lookup is not None
        assert lookup.lookup_uuid == encounter_uuid
        assert lookup.file_name == f"{mrn}-{epr_encounter_id}.pdf"

        assert mock_write.call_count == 2

    def test_create_secondary_send_documents_success(
        self,
        sample_send_data: Dict,
        trustomer_config: Dict,
        requests_mock: Mocker,
        mocker: MockFixture,
    ) -> None:
        sample_data = copy.deepcopy(sample_send_data)
        sample_data["encounter"]["discharged_at"] = "2019-01-26T10:01:10.000Z"
        expected_data = copy.deepcopy(sample_data)
        mrn = sample_data["patient"]["hospital_number"]
        epr_encounter_id = sample_data["encounter"]["epr_encounter_id"]

        mock_post: Any = requests_mock.post(
            f"http://localhost:3000/dhos/v1/send_pdf",
            headers={"Content-Type": "application/pdf"},
            content=b"something",
            status_code=200,
        )

        mock_write = mocker.patch.object(controller, "write_file")
        mocker.patch("os.path.isdir", return_value=False)
        mocker.patch("os.mkdir")

        controller.create_send_documents(sample_data)
        assert mock_post.call_count == 1
        assert mock_post.last_request.json() == expected_data

        encounter_uuid = sample_data["encounter"]["uuid"]
        lookup = FilenameLookup.query.filter_by(lookup_uuid=encounter_uuid).first()
        assert lookup is not None
        assert lookup.lookup_uuid == encounter_uuid
        assert lookup.file_name == f"{mrn}-{epr_encounter_id}.pdf"

        assert mock_write.call_count == 4

    def test_create_send_documents_http_error(
        self, sample_send_data: Dict, requests_mock: Mocker
    ) -> None:
        requests_mock.post(f"http://localhost:3000/dhos/v1/send_pdf", status_code=500)
        with pytest.raises(ServiceUnavailableException):
            controller.create_send_documents(sample_send_data)

    def test_create_send_pdf_http_error(
        self, sample_send_data: Dict, requests_mock: Mocker
    ) -> None:
        requests_mock.post(f"http://localhost:3000/dhos/v1/send_pdf", status_code=500)
        with pytest.raises(ServiceUnavailableException):
            controller.create_send_documents(sample_send_data)

    def test_create_send_documents_connection_error(
        self, sample_send_data: Dict, requests_mock: Mocker
    ) -> None:
        requests_mock.post(
            f"http://localhost:3000/dhos/v1/send_pdf",
            exc=requests.exceptions.ConnectionError(),
        )
        with pytest.raises(ServiceUnavailableException):
            controller.create_send_documents(sample_send_data)

    def test_create_send_documents_no_obs(
        self,
        sample_send_data: Dict,
        requests_mock: Mocker,
        mocker: MockFixture,
        caplog: Any,
    ) -> None:
        sample_send_data["observation_sets"] = []
        sample_send_data["encounter"]["score_system_history"] = []

        mock_post: Any = requests_mock.post(f"http://localhost:3000/dhos/v1/send_pdf")
        mock_write: Mock = mocker.patch.object(controller, "write_file")

        controller.create_send_documents(sample_send_data)
        assert mock_post.call_count == 0

        encounter_uuid = sample_send_data["encounter"]["uuid"]
        lookup = FilenameLookup.query.filter_by(lookup_uuid=encounter_uuid).first()
        assert lookup is None
        assert mock_write.call_count == 0
        assert caplog.records[-1].message.startswith(
            "Skipping SEND document generation"
        )

    def test_create_send_documents_overwrite_existing(
        self, sample_send_data: Dict, requests_mock: Mocker, mocker: MockFixture
    ) -> None:
        encounter_uuid = sample_send_data["encounter"]["uuid"]
        lookup_uuid = generate_uuid()
        mrn = sample_send_data["patient"]["hospital_number"]
        epr_encounter_id = sample_send_data["encounter"]["epr_encounter_id"]

        # Add preexisting filename to database
        first = FilenameLookup(
            uuid=lookup_uuid, file_name="old.pdf", lookup_uuid=encounter_uuid
        )
        db.session.add(first)
        db.session.commit()

        mock_post: Any = requests_mock.post(
            f"http://localhost:3000/dhos/v1/send_pdf",
            headers={"Content-Type": "application/pdf"},
            content=b"something",
            status_code=200,
        )

        mock_write = mocker.patch.object(controller, "write_file")
        mocker.patch("os.path.isdir", return_value=False)
        mocker.patch("os.mkdir")

        controller.create_send_documents(sample_send_data)
        assert mock_post.call_count == 1
        assert mock_post.last_request.json() == sample_send_data

        lookup = FilenameLookup.query.filter_by(lookup_uuid=encounter_uuid).first()
        assert lookup is not None
        assert lookup.uuid == lookup_uuid
        assert lookup.lookup_uuid == encounter_uuid
        assert lookup.file_name == f"{mrn}-{epr_encounter_id}.pdf"

        assert mock_write.call_count == 2

    def test_get_pdf_path_from_encounter_uuid(
        self, sample_send_data: Dict, mocker: MockFixture
    ) -> None:
        # Arrange
        encounter_uuid = sample_send_data["encounter"]["uuid"]
        expected_path = "some.pdf"
        pdf_bytes = b"1" * 10
        first = FilenameLookup(
            uuid=generate_uuid(), file_name=expected_path, lookup_uuid=encounter_uuid
        )
        db.session.add(first)
        db.session.commit()
        mock_read: Mock = mocker.patch.object(
            Path,
            "read_bytes",
            return_value=pdf_bytes,
        )

        # Act
        content = controller.get_send_pdf(encounter_uuid)

        # Assert
        assert content == pdf_bytes
        assert mock_read.call_count == 1

    def test_pdf_stream(self) -> None:
        byte_array = b"1" * 1000
        chunk_size = 100

        response = controller.pdf_stream(byte_array, chunk_size)
        print(response.data)

        assert len([chunk for chunk in response.iter_encoded()]) == 10

    @pytest.mark.parametrize("date_of_birth", ["1985-07-01", None])
    def test_create_pdf_metadata_xml(
        self, sample_send_data: Dict, mocker: MockFixture, date_of_birth: Optional[str]
    ) -> None:
        nowtime = "2019-01-26T10:01:10.000Z"
        mocker.patch(
            "dhos_pdf_api.blueprint_api.controller.get_iso_format_time_now",
            return_value=nowtime,
        )
        if date_of_birth is None:
            date_of_birth = ""
        else:
            date_of_birth = date_of_birth.replace("-", "")

        expected = (
            '<xml version="1.0" encoding="UTF-8" >'
            + "<Docinfo><ExternalReferenceNumber>2018L73782250</ExternalReferenceNumber>"
            + "<Documentfilename>2018L73782250.pdf</Documentfilename>"
            + "<DocumentTypeCode>01</DocumentTypeCode>"
            + "<DocumentCreatedDateTime>20190126 10:01:10</DocumentCreatedDateTime>"
            + "<DocumentAuthor>SEND</DocumentAuthor></Docinfo>"
            + "<PatientInfo><PatientEpisodeId>2018L73782250</PatientEpisodeId>"
            + "<PatientForename>Michele</PatientForename>"
            + "<PatientSurname>Haynes</PatientSurname>"
            + f"<PatientDOB>{date_of_birth}</PatientDOB>"
            + "<PatientNHSNumber>9991677789</PatientNHSNumber>"
            + "<PatientURNumber>27988932</PatientURNumber>"
            + "<PatientGender>Female</PatientGender>"
            + "<PatientAdmissionDateTime>20190125 00:00:00</PatientAdmissionDateTime>"
            + "<PatientDischargeDateTime></PatientDischargeDateTime>"
            + "<SpecialtyCode></SpecialtyCode><SpecialtyName></SpecialtyName>"
            + "</PatientInfo><GPPractice><PracticeName></PracticeName><GpName></GpName>"
            + "<PracticeNacsCode></PracticeNacsCode></GPPractice></xml>"
        )
        xml_data = copy.deepcopy(sample_send_data)
        xml_data["pdf_filename"] = "2018L73782250.pdf"
        xml_data["encounter_id"] = "2018L73782250"
        response = controller.create_pdf_metadata_xml(xml_data)
        assert response == bytes(expected, "utf-8")

    def test_save_filename_lookup(self, mocker: MockFixture) -> None:
        """
        Tests that when there's no existing FilenameLookup to update, we try to create a new one.
        """
        # Arrange
        lookup_uuid: str = generate_uuid()
        mock_create: Mock = mocker.patch.object(
            controller, "_create_new_filename_lookup"
        )

        # Act
        controller._save_filename_lookup(lookup_uuid=lookup_uuid, file_name="new.pdf")

        # Assert
        assert mock_create.call_count == 1

    def test_create_new_filename_lookup_with_threading_clash(
        self, caplog: LogCaptureFixture
    ) -> None:
        """
        Tests that when there's a IntegrityError on creating a new FilenameLookup (due to database
        action on another thread or in another pod), we try again to commit the update.
        """
        lookup_uuid: str = generate_uuid()
        lookup = FilenameLookup(
            uuid=generate_uuid(), lookup_uuid=lookup_uuid, file_name="old.txt"
        )
        db.session.add(lookup)
        db.session.commit()
        controller._create_new_filename_lookup(
            lookup_uuid=lookup_uuid, file_name="new.txt"
        )
        assert "Failed to create FilenameLookup" in caplog.text
        assert (
            FilenameLookup.query.filter_by(lookup_uuid=lookup_uuid).first().file_name
            == "new.txt"
        )
