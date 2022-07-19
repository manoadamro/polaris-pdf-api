import re
from io import BytesIO
from typing import Dict, List

import pdfplumber
from behave import given, step
from behave.runner import Context
from clients.dhos_pdf_client import get_dbm_patient_pdf, post_dbm_pdf_request
from helpers.dbm_patient_helper import generate_dbm_patient
from pdfplumber.pdf import PDF
from requests import Response


@given("there exists a dbm patient {withorwithout} hba1c")
def get_dbm_body(context: Context, withorwithout: str) -> None:
    patient = generate_dbm_patient()
    if withorwithout == "without":
        del patient["hba1c_details"]
    context.patient_body = patient


@step("a request to create a PDF document for dbm patient is made")
def send_create_request(context: Context) -> None:
    context.create_pdf_response = post_dbm_pdf_request(
        jwt=context.system_jwt, patient_data=context.patient_body
    )


@step("the dbm patient PDF {withorwithout} hba1c can be retrieved by patient uuid")
def get_dbm_pdf(context: Context, withorwithout: str) -> None:
    hba1c = True if withorwithout == "with" else False
    response: Response = get_dbm_patient_pdf(
        jwt=context.system_jwt, patient_uuid=context.patient_body["patient"]["uuid"]
    )
    response.raise_for_status()
    assert response.headers["content-type"] == "application/pdf"

    with pdfplumber.open(BytesIO(response.content)) as pdf:
        assert len(pdf.pages) == 1
        t = _extract_document_text(pdf)
        u = _unfiltered_document_text(pdf)
        _assert_patient_details(context=context, text=t, unfiltered=u, hba1c=hba1c)


def _extract_document_text(pdf: PDF) -> Dict[str, str]:
    # extract from PDF anything that looks like <key>:<non-null value> and return a dict of it
    all_text: List[str] = [
        text
        for page in pdf.pages
        for text in page.extract_text().split("\n")
        if re.search(r":\s", text)
    ]
    return {k: v for k, v in [re.split(r":\s+", text, 1) for text in all_text]}


def _unfiltered_document_text(pdf: PDF) -> List[str]:
    return pdf.pages[0].extract_text().split("\n")


def _assert_patient_details(
    context: Context, text: Dict[str, str], unfiltered: List[str], hba1c: bool
) -> None:
    assert "2021-08-29 20:40:07.498 4.5 here's a comment" in unfiltered
    assert (
        f"{context.patient_body['patient']['first_name']} {context.patient_body['patient']['last_name']}"
        == text["Name"]
    )
    assert context.patient_body["patient"]["nhs_number"] == text["NHS number"]
    assert context.patient_body["patient"]["hospital_number"] == text["MRN"]
    if hba1c:
        assert "29.0 mmol/mol 2021-02-20" in unfiltered
