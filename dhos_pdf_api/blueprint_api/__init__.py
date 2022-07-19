from pathlib import Path
from typing import Dict

from flask import Blueprint, Response, current_app, make_response
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import scopes_present
from she_logging import logger

from dhos_pdf_api.blueprint_api import controller
from dhos_pdf_api.models.api_spec import (
    DbmPdfRequestSchema,
    GdmPdfRequestSchema,
    SendPdfRequestSchema,
    WardReportRequestSchema,
)

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/gdm_pdf", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:gdm_pdf"))
def create_gdm_patient_pdf(gdm_patient_details: Dict) -> Response:
    """---
    post:
      summary: Create new PDF document containing a summary of a GDM patient record
      description: >-
        Generate a PDF containing a summary of a GDM patient record. The request body contains
        details of the patient and their blood glucose readings. Responds with HTTP 201.
      tags: [pdf]
      requestBody:
        description: Data for creation of patient report
        required: true
        content:
          application/json:
            schema:
                x-body-name: gdm_patient_details
                $ref: '#/components/schemas/GdmPdfRequestSchema'
      responses:
        '201':
          description: PDF document created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    logger.debug(f"gdm_patient_details: {gdm_patient_details}")
    pdf_data: Dict = GdmPdfRequestSchema().load(gdm_patient_details)
    controller.create_patient_pdf(data=pdf_data, product_name="gdm")
    return make_response("", 201)


@api_blueprint.route("/dbm_pdf", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:gdm_pdf"))
def create_patient_pdf(patient_details: Dict) -> Response:
    """---
    post:
      summary: >-
        Create new DBM PDF document containing a summary of the patient record
      description: >-
        Generate a PDF containing a summary of a DBM patient record. The request body contains
        details of the patient and their blood glucose readings. Responds with HTTP 201.
      tags: [pdf]
      requestBody:
        description: Data for creation of patient report
        required: true
        content:
          application/json:
            schema:
              x-body-name: patient_details
      responses:
        '201':
          description: PDF document created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    patient_details = DbmPdfRequestSchema().load(patient_details)
    controller.create_patient_pdf(data=patient_details, product_name="dbm")
    return make_response("", 201)


@api_blueprint.route("/gdm_pdf/<patient_uuid>", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:gdm_pdf"))
def get_gdm_patient_pdf(patient_uuid: str) -> Response:
    """---
    get:
      summary: Get GDM PDF by patient UUID
      description: >-
        Get a care record PDF for a GDM patient with the provided patient UUID
      tags: [pdf]
      parameters:
        - name: patient_uuid
          in: path
          required: true
          description: The patient UUID
          schema:
            type: string
            example: '1e4e623e-d918-448a-ba13-393408160354'
      responses:
        '200':
          description: The requested PDF document
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/pdf:
              schema: Error
    """
    content: bytes = controller.get_patient_pdf(
        patient_uuid=patient_uuid, product_name="gdm"
    )
    return controller.pdf_stream(content)


@api_blueprint.route("/dbm_pdf/<patient_uuid>", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:gdm_pdf"))
def get_patient_pdf(patient_uuid: str) -> Response:
    """---
    get:
      summary: Get DBM PDF by patient UUID
      description: >-
        Get a DBM care record PDF for a patient with the provided patient UUID
      tags: [pdf]
      parameters:
        - name: patient_uuid
          in: path
          required: true
          description: The patient UUID
          schema:
            type: string
            example: '1e4e623e-d918-448a-ba13-393408160354'
      responses:
        '200':
          description: The requested PDF document
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/pdf:
              schema: Error
    """
    content: bytes = controller.get_patient_pdf(
        patient_uuid=patient_uuid, product_name="dbm"
    )
    return controller.pdf_stream(content)


@api_blueprint.route("/send_pdf", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:send_pdf"))
def create_send_documents(send_documents_details: Dict) -> Response:
    """---
    post:
      summary: Create new PDF document containing observations for a SEND patient
      description: >-
        Generate a PDF chart for a SEND patient, containing observations recorded during a particular encounter (hospital stay). This endpoint may also generate additional files depending on the trustomer configuration. The endpoint responds with an HTTP 201 on success.
      tags: [pdf]
      requestBody:
        description: Data for creation of SEND report
        required: true
        content:
          application/json:
            schema:
                x-body-name: send_documents_details
                $ref: '#/components/schemas/SendPdfRequestSchema'
      responses:
        '201':
          description: PDF document created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    data: Dict = SendPdfRequestSchema().load(send_documents_details)
    controller.create_send_documents(data)
    return make_response("", 201)


@api_blueprint.route("/patient/pdf/<encounter_uuid>", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:send_pdf"))
def get_send_patient_pdf(encounter_uuid: str) -> Response:
    """---
    get:
      summary: Get SEND PDF by encounter UUID
      description: >-
        Get a PDF chart for a SEND patient for the provided encounter (hospital stay) UUID.
      tags: [pdf]
      parameters:
        - name: encounter_uuid
          in: path
          required: true
          description: The encounter (hospital stay) UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
      responses:
        '200':
          description: The requested PDF document
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/pdf:
              schema: Error
    """
    content: bytes = controller.get_send_pdf(encounter_uuid)
    return controller.pdf_stream(content)


@api_blueprint.route("/ward_report", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:ward_report"))
def create_ward_report(ward_report_details: Dict) -> Response:
    """---
    post:
      summary: Create new PDF document for a SEND ward report for the provided location
      description: >-
        Generate a SEND PDF ward report for a particular location, containing statistics on the observations taken for patients in that location. The endpoint responds with an HTTP 201 on success.
      tags: [pdf]
      requestBody:
        description: Data for creation of ward report
        required: true
        content:
          application/json:
            schema:
                x-body-name: ward_report_details
                $ref: '#/components/schemas/WardReportRequestSchema'
      responses:
        '201':
          description: PDF document created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    data = WardReportRequestSchema().load(ward_report_details)
    controller.generate_send_ward_report_pdf(
        data, ward_report_folder=Path(current_app.config["SEND_WARD_REPORT_OUTPUT_DIR"])
    )
    return make_response("", 201)


@api_blueprint.route("/ward_report/<location_uuid>", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:ward_report"))
def get_ward_report(location_uuid: str) -> Response:
    """---
    get:
      summary: Get SEND ward report PDF by location UUID
      description: >-
        Get a SEND PDF ward report for the provided location UUID.
      tags: [pdf]
      parameters:
        - name: location_uuid
          in: path
          required: true
          description: The location UUID for the hospital ward
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
      responses:
        '200':
          description: The requested PDF document
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/pdf:
              schema: Error
    """
    content: bytes = controller.get_send_ward_report_pdf(
        location_uuid,
        ward_report_folder=Path(current_app.config["SEND_WARD_REPORT_OUTPUT_DIR"]),
    )
    return controller.pdf_stream(content)
