from io import BytesIO

import pdfplumber
from behave import given, step
from behave.runner import Context
from clients.dhos_pdf_client import get_send_patient_pdf, post_send_pdf_request
from helpers.send_patient_helper import generate_send_patient
from requests import Response


@given("there exists a SEND patient")
def get_send_body(context: Context) -> None:
    context.patient_body = generate_send_patient()


@step("a request to create a PDF document for SEND patient is made")
def send_create_request(context: Context) -> None:
    context.create_pdf_response = post_send_pdf_request(
        jwt=context.system_jwt, patient_data=context.patient_body
    )


@step("the SEND patient PDF can be retrieved by its encounter uuid")
def get_send_pdf(context: Context) -> None:
    response: Response = get_send_patient_pdf(
        jwt=context.system_jwt, encounter_uuid=context.patient_body["encounter"]["uuid"]
    )
    response.raise_for_status()
    assert response.headers["content-type"] == "application/pdf"

    with pdfplumber.open(BytesIO(response.content)) as pdf:
        assert len(pdf.pages) == 4
        # SEND PDF document is pretty complex, with very few values being listed with
        # corresponding labels, hence verify only that the headline page of the retrieved PDF
        # contains the patient's data
        page_text = pdf.pages[0].extract_text()

        assert (
            f"Name:{context.patient_body['patient']['last_name'].upper()}, {context.patient_body['patient']['first_name']}"
            in page_text
        )
        assert f"MRN: {context.patient_body['patient']['hospital_number']}" in page_text
        assert f"Ward: {context.patient_body['location']['display_name']}" in page_text
