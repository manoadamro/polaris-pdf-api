import logging
from io import BytesIO

from behave import given, step
from behave.runner import Context
from clients.dhos_pdf_client import get_ward_report_pdf, post_ward_report_request
from helpers.ward_report_helper import generate_ward_report
from requests import Response

logging.getLogger("pdfminer").setLevel(logging.WARNING)
import pdfplumber


@given("ward metrics have been generated")
def get_ward_metrics_body(context: Context) -> None:
    context.request_body = generate_ward_report()


@step("a request to create a ward report is made")
def create_ward_report_request(context: Context) -> None:
    context.create_pdf_response = post_ward_report_request(
        jwt=context.system_jwt, metrics_data=context.request_body
    )


@step("the ward report PDF can be retrieved by its location uuid")
def get_ward_pdf(context: Context) -> None:
    response: Response = get_ward_report_pdf(
        jwt=context.system_jwt, location_uuid=context.request_body["location_uuid"]
    )
    response.raise_for_status()
    assert response.headers["content-type"] == "application/pdf"

    with pdfplumber.open(BytesIO(response.content)) as pdf:
        assert len(pdf.pages) == 1
        page_text = [
            text for page in pdf.pages for text in page.extract_text().split("\n")
        ]
        # pdfplumber doesn't know how to handle non-ascii characters (it returns them as spaces)
        hospital = (
            context.request_body["hospital_name"]
            .encode("ascii", "replace")
            .decode("ascii")
            .replace("?", " ")
        )
        ward = (
            context.request_body["ward_name"]
            .encode("ascii", "replace")
            .decode("ascii")
            .replace("?", " ")
        )
        assert f"{hospital.strip()} {ward.strip()}" in page_text, page_text[0]
        assert (
            f"{context.request_body['report_month']} {context.request_body['report_year']}"
            in page_text
        )


@given("there exist many ward metrics")
def get_ward_metrics_bodies(context: Context) -> None:
    context.request_body = [
        generate_ward_report(days=5, locale="hr_HR", force_zero=True) for _ in range(10)
    ]


@step("requests to create ward reports are made")
def create_ward_report_requests(context: Context) -> None:
    for data in context.request_body:
        context.create_pdf_response = post_ward_report_request(
            jwt=context.system_jwt, metrics_data=data
        )
        assert context.create_pdf_response.status_code == 201
