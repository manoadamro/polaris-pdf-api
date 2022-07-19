import re
from io import BytesIO
from typing import Dict, List

import pdfplumber
from behave import given, step
from behave.runner import Context
from clients.dhos_pdf_client import get_gdm_patient_pdf, post_gdm_pdf_request
from helpers.gdm_patient_helper import generate_gdm_patient
from pdfplumber.pdf import PDF
from requests import Response


@given("there exists a GDM patient")
def get_gdm_body(context: Context) -> None:
    context.patient_body = generate_gdm_patient()


@step("a request to create a PDF document for GDM patient is made")
def send_create_request(context: Context) -> None:
    context.create_pdf_response = post_gdm_pdf_request(
        jwt=context.system_jwt, patient_data=context.patient_body
    )


@step("the response is valid")
def assert_create_request_response(context: Context) -> None:
    assert (
        context.create_pdf_response.status_code == 201
    ), context.create_pdf_response.status_code


@step("the GDM patient PDF can be retrieved by patient uuid")
def get_gdm_pdf(context: Context) -> None:
    response: Response = get_gdm_patient_pdf(
        jwt=context.system_jwt, patient_uuid=context.patient_body["patient"]["uuid"]
    )
    response.raise_for_status()
    assert response.headers["content-type"] == "application/pdf"

    with pdfplumber.open(BytesIO(response.content)) as pdf:
        assert len(pdf.pages) == 3
        t = _extract_document_text(pdf)
        _assert_patient_details(context=context, text=t)
        assert "midwife" in pdf.pages[1].extract_text()
        assert "Testing first message" in pdf.pages[2].extract_text()
        assert "Testing second message" in pdf.pages[2].extract_text()


def _extract_document_text(pdf: PDF) -> Dict[str, str]:
    # extract from PDF anything that looks like <key>:<non-null value> and return a dict of it
    all_text: List[str] = [
        text
        for page in pdf.pages
        for text in page.extract_text().split("\n")
        if re.search(r":\s", text)
    ]
    return {k: v for k, v in [re.split(r":\s+", text, 1) for text in all_text]}


def _assert_patient_details(context: Context, text: Dict[str, str]) -> None:
    assert (
        f"{context.patient_body['patient']['first_name']} {context.patient_body['patient']['last_name']}"
        == text["Name"]
    )
    assert context.patient_body["patient"]["nhs_number"] == text["NHS number"]
    assert context.patient_body["patient"]["hospital_number"] == text["MRN"]
    assert (
        context.patient_body["post_natal_reading"]["date"]
        == text["Date of post-natal test"]
    )
