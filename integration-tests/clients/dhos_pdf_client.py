from typing import Dict

import requests
from environs import Env
from requests import Response


def _get_base_url() -> str:
    return Env().str("DHOS_PDF_BASE_URL", "http://dhos-pdf-api:5000")


def post_gdm_pdf_request(patient_data: Dict, jwt: str) -> Response:
    return requests.post(
        url=f"{_get_base_url()}/dhos/v1/gdm_pdf",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=patient_data,
    )


def post_send_pdf_request(patient_data: Dict, jwt: str) -> Response:
    return requests.post(
        url=f"{_get_base_url()}/dhos/v1/send_pdf",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=patient_data,
    )


def post_ward_report_request(metrics_data: Dict, jwt: str) -> Response:
    return requests.post(
        url=f"{_get_base_url()}/dhos/v1/ward_report",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=metrics_data,
    )


def get_gdm_patient_pdf(patient_uuid: str, jwt: str) -> Response:
    return requests.get(
        url=f"{_get_base_url()}/dhos/v1/gdm_pdf/{patient_uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def get_send_patient_pdf(encounter_uuid: str, jwt: str) -> Response:
    return requests.get(
        url=f"{_get_base_url()}/dhos/v1/patient/pdf/{encounter_uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def get_ward_report_pdf(location_uuid: str, jwt: str) -> Response:
    return requests.get(
        url=f"{_get_base_url()}/dhos/v1/ward_report/{location_uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def get_dbm_patient_pdf(patient_uuid: str, jwt: str) -> Response:
    return requests.get(
        url=f"{_get_base_url()}/dhos/v1/dbm_pdf/{patient_uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def post_dbm_pdf_request(patient_data: Dict, jwt: str) -> Response:
    return requests.post(
        url=f"{_get_base_url()}/dhos/v1/dbm_pdf",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=patient_data,
    )
