"""
HL7 Continuity of Care Document

This module generates an HL7 CDA Continuity of Care Document (CCD).

The full CDA CCD specification may be found on www.hl7.org, but that document covers a wide variety of information.
We are only interested here in producing a document that will link the patient encounter to the PDF file we have
generated.

This document includes summary information about the patient, a clinician involved with the patient (either
the first clinician to take observations within this encounter, or the clinician who created the encounter if there
are no observations), the patient's location, the EPR encounter id, and of course the path to the PDF document.
"""
from pathlib import PurePath, PureWindowsPath
from typing import Dict
from xml.etree.ElementTree import Element, SubElement, register_namespace, tostring

import draymed
from flask_batteries_included.helpers.timestamp import parse_iso8601_to_datetime
from lxml import etree
from she_logging import logger

from dhos_pdf_api.blueprint_api.helpers import get_datetime_now, xml_datetime_convert

# N.B. The commented out out Java code below is taken from the original SEND product.
# It is left here for easy comparison, but at some point (once we are confident everything was ported correctly)
# we should remove it.

HL7_ADMINISTRATIVE_GENDER = "2.16.840.1.113883.5.1"
HL7_ADMINISTRATIVE_SEX = "2.16.840.1.113883.2.1.3.2.4.16.25"
HL7_NHS_NUMBER = "2.16.840.1.113883.2.1.4.1"
HL7_EXTERNAL_IDENTIFICATION_SCHEME = "2.16.840.1.113883.4"
HL7_REFINED_MESSAGE_INFORMATION_MODELS = "2.16.840.1.113883.1.3"

DATETIME_FORMAT = "%Y%m%d%H%M%S"
DATE_FORMAT = "%Y%m%d"

register_namespace("", "urn:hl7-org:v3")


def xml_person_name(parent: Element, person: Dict) -> Element:
    name = SubElement(parent, "name")
    SubElement(
        name, "given", partType="GIV", representation="TXT", mediaType="text/plain"
    ).text = person.get("first_name")
    SubElement(
        name, "family", partType="FAM", representation="TXT", mediaType="text/plain"
    ).text = person.get("last_name")
    return name


def create_hl7_cda_xml(
    data: dict, base_unc_path: str, pdf_filename: str, parser: object
) -> bytes:
    encounter: dict = data.get("encounter", {})
    patient: dict = data.get("patient", {})

    root = Element(
        "{urn:hl7-org:v3}ClinicalDocument", classCode="DOCCLIN", moodCode="EVN"
    )
    _append_header_elements(encounter, root)

    _append_patient_element(patient, root)
    _append_author_element(data, encounter, root)

    _append_custodian_element(data, root)
    _append_component1_encounter(encounter, root)
    _append_component2_pdf_document(
        PureWindowsPath(base_unc_path) / pdf_filename, data, root
    )

    logger.debug("Created HL7 XML CDA")
    xml = tostring(root, encoding="utf8")
    _validate_xml(xml, parser)
    return xml


def _append_header_elements(encounter: dict, root: Element) -> None:
    # 				InfrastructureRootTypeId typeId = this.cdaFactory.createInfrastructureRootTypeId();
    # 				typeId.setRoot("2.16.840.1.113883.1.3");
    # 				typeId.setExtension("POCD_HD000040");
    # 				ccdDocument.setTypeId(typeId);
    SubElement(
        root,
        "typeId",
        root=HL7_REFINED_MESSAGE_INFORMATION_MODELS,
        extension="POCD_HD000040",
    )
    #
    # 				ccdDocument.getTemplateIds().clear();
    #
    # 				II documentId = this.datatypesFactory.createII("2.16.840.1.113883.4", encounterModel.getEncounterId());
    # 				documentId.setAssigningAuthorityName("PAS");
    # 				ccdDocument.setId(documentId);
    #
    SubElement(
        root,
        "id",
        root=HL7_EXTERNAL_IDENTIFICATION_SCHEME,
        extension=encounter.get("epr_encounter_id", "") or encounter.get("uuid", ""),
        assigningAuthorityName="PAS",
    )
    # 				CE code = this.datatypesFactory.createCE("pdf-cda-tt-chart", "OCI", "Case Notes", "NEWS Chart");
    # 				ccdDocument.setCode(code);
    SubElement(
        root,
        "code",
        code="pdf-cda-news2-chart",
        codeSystem="OCI",
        codeSystemName="Case Notes",
        displayName="NEWS2 Chart",
    )
    #
    # 				ST documentTitle = this.datatypesFactory.createST("NEWS Chart");
    # 				ccdDocument.setTitle(documentTitle);
    SubElement(
        root, "title", representation="TXT", mediaType="text/plain"
    ).text = "NEWS2 Chart"
    #
    # 				TS effectiveTime = this.datatypesFactory.createTS(DATETIME_FORMAT.format(encounterModel.getCreated()));
    # 				ccdDocument.setEffectiveTime(effectiveTime);
    SubElement(
        root, "effectiveTime", value=get_datetime_now().strftime(DATETIME_FORMAT)
    )
    #
    # 				CE confidentialityCode = this.datatypesFactory.createCE();
    # 				ccdDocument.setConfidentialityCode(confidentialityCode);
    SubElement(root, "confidentialityCode")


def _append_patient_element(patient: dict, root: Element) -> None:
    record_target = SubElement(
        root, "recordTarget", typeCode="RCT", contextControlCode="OP"
    )
    #
    # 				// create a patient role object and add it to the document
    # 				PatientRole patientRole = this.cdaFactory.createPatientRole();
    patient_role = SubElement(record_target, "patientRole", classCode="PAT")
    #
    # 				for (PatientIdentifierModel identifier : encounterModel.getPatient().getIdentifiers())
    # 				{
    # 					String oid = ("NHS".equals(identifier.getIdentifierType().getCode()) ? "2.16.840.1.113883.2.1.4.1" : "2.16.840.1.113883.4");
    # 					II number = this.datatypesFactory.createII(oid, identifier.getIdentifier());
    # 					number.setAssigningAuthorityName(identifier.getIdentifierType().getCode());
    # 					patientRole.getIds().add(number);
    # 				}
    #
    for patient_id, oid, assigning_authority in [
        (patient.get("nhs_number"), HL7_NHS_NUMBER, "NHS"),
        (patient.get("hospital_number"), HL7_EXTERNAL_IDENTIFICATION_SCHEME, "PAS"),
    ]:
        if patient_id is not None:
            SubElement(
                patient_role,
                "id",
                root=oid,
                extension=patient_id,
                assigningAuthorityName=assigning_authority,
            )
    patient_el = SubElement(
        patient_role, "patient", classCode="PSN", determinerCode="INSTANCE"
    )
    # 				// create a patient object and add it to patient role
    # 				Patient patient = this.cdaFactory.createPatient();
    # 				PN name = this.datatypesFactory.createPN();
    # 				patient.getNames().add(name);
    # 				name.addGiven(patientModel.getForename());
    # 				name.addFamily(patientModel.getSurname());
    xml_person_name(patient_el, patient)
    #
    # 				patientRole.setPatient(patient);
    # 				ccdDocument.addPatientRole(patientRole);
    #
    # 				GenderModel genderModel = patientModel.getGender();
    # 				CE administrativeGenderCode = this.datatypesFactory.createCE(genderModel.getCode(), "2.16.840.1.113883.2.1.3.2.4.16.25");
    # 				patient.setAdministrativeGenderCode(administrativeGenderCode);
    sex_abbreviation = draymed.codes.description_from_code(
        patient.get("sex", ""), category="sex"
    )[0].title()
    SubElement(
        patient_el,
        "administrativeGenderCode",
        code=sex_abbreviation,
        codeSystem=HL7_ADMINISTRATIVE_SEX,
    )
    #
    # 				TS birthTime = this.datatypesFactory.createTS(DATE_FORMAT.format(patientModel.getDob()));
    # 				patient.setBirthTime(birthTime);
    dob = patient.get("dob")
    if dob is not None:
        xml_dob = xml_datetime_convert(dob)
        if xml_dob is not None:
            SubElement(patient_el, "birthTime", value=xml_dob)


def _append_author_element(data: dict, encounter: dict, root: Element) -> None:
    #
    # 				// Expand Author Information (ID, Forename, Surname etc)
    # 				Person person = this.cdaFactory.createPerson();
    # 				II authorId = this.datatypesFactory.createII("2.16.840.1.113883.4");
    #
    # 				AssignedAuthor assignedAuthor = this.cdaFactory.createAssignedAuthor();
    # 				assignedAuthor.getIds().add(authorId);
    # 				assignedAuthor.setAssignedPerson(person);
    #
    # 				// Set Document Author
    # 				TS authoredTime = this.datatypesFactory.createTS(DATETIME_FORMAT.format(encounterModel.getCreated()));
    #
    # 				Author author = this.cdaFactory.createAuthor();
    # 				author.setTime(authoredTime);
    # 				author.setAssignedAuthor(assignedAuthor);
    # 				ccdDocument.getAuthors().add(author);
    author = SubElement(root, "author", typeCode="AUT", contextControlCode="OP")
    created = parse_iso8601_to_datetime(encounter["created"])
    if created is None:
        raise ValueError("created is None")
    SubElement(author, "time", value=created.strftime(DATETIME_FORMAT))
    assigned_author = SubElement(author, "assignedAuthor", classCode="ASSIGNED")
    #
    # 				if (!encounterModel.getObservationSessions().isEmpty())
    # 				{
    # 					ObservationSessionModel observationSessionModel = encounterModel.getObservationSessions().get(0);
    # 					UserModel userModel = observationSessionModel.getUser();
    #
    # 					if (StringUtils.isNotEmpty(userModel.getSmartcardId()))
    # 					{
    # 						authorId.setExtension(userModel.getSmartcardId());
    # 						authorId.setAssigningAuthorityName("NHS");
    # 					}
    # 					else
    # 					{
    # 						LOG.warn(String.format("User %1$s does not have a smartcard identifier defined", new Object[] {userModel.getUsername()}));
    # 						authorId.setExtension(String.valueOf(userModel.getId()));
    # 						authorId.setAssigningAuthorityName("SEND");
    # 					}
    #
    # 					PN personName = this.datatypesFactory.createPN();
    # 					personName.addGiven(userModel.getForename());
    # 					personName.addFamily(userModel.getSurname());
    # 					person.getNames().add(personName);
    # 				}
    # 				else if (encounterModel.getConsultant() != null)
    # 				{
    # 					ConsultantModel consultantModel = encounterModel.getConsultant();
    # 					authorId.setExtension(consultantModel.getIdentifier());
    # 					authorId.setAssigningAuthorityName("NHS");
    #
    # 					PN personName = this.datatypesFactory.createPN();
    # 					personName.addGiven(consultantModel.getForename());
    # 					personName.addFamily(consultantModel.getSurname());
    # 					person.getNames().add(personName);
    # 				}
    obs_sets = data.get("observation_sets")
    if obs_sets:
        creator = obs_sets[0].get("created_by")
    else:
        creator = encounter.get("created_by")

    uuid = creator.get("uuid")
    if uuid is not None:
        SubElement(
            assigned_author,
            "id",
            root=HL7_EXTERNAL_IDENTIFICATION_SCHEME,
            extension=creator["uuid"],
            assigningAuthorityName="SEND",
        )
        person = SubElement(
            assigned_author,
            "assignedPerson",
            classCode="PSN",
            determinerCode="INSTANCE",
        )
        xml_person_name(person, creator)


def _find_top_level_location(location: Dict) -> Dict:
    if location.get("parent") is None:
        return location

    return _find_top_level_location(location["parent"])


def _append_custodian_element(data: dict, root: Element) -> None:
    #
    # 				LocationModel location = encounterModel.getLocation();
    # 				OrganisationModel organisationModel = location.getOrganisation();
    # 				CustodianOrganization custodianOrganization = this.cdaFactory.createCustodianOrganization();
    # 				II organisationId = this.datatypesFactory.createII("2.16.840.1.113883.4", organisationModel.getCode());
    # 				organisationId.setAssigningAuthorityName("OUH");
    # 				custodianOrganization.getIds().add(organisationId);
    #
    # 				ON organisationName = this.datatypesFactory.createON();
    # 				organisationName.addText(organisationModel.getName());
    # 				custodianOrganization.setName(organisationName);
    #
    # 				AssignedCustodian assignedCustodian = this.cdaFactory.createAssignedCustodian();
    # 				assignedCustodian.setRepresentedCustodianOrganization(custodianOrganization);
    #
    # 				Custodian custodian = this.cdaFactory.createCustodian();
    # 				custodian.setAssignedCustodian(assignedCustodian);
    # 				ccdDocument.setCustodian(custodian);

    # Location may be bay, bed, or ward so find the ultimate parent location as that's what we
    # want to use
    location = _find_top_level_location(data["location"])

    custodian = SubElement(root, "custodian", typeCode="CST")
    assigned_custodian = SubElement(
        custodian, "assignedCustodian", classCode="ASSIGNED"
    )
    custodian_organization = SubElement(
        assigned_custodian,
        "representedCustodianOrganization",
        classCode="ORG",
        determinerCode="INSTANCE",
    )
    SubElement(
        custodian_organization,
        "id",
        root=HL7_EXTERNAL_IDENTIFICATION_SCHEME,
        extension=location["ods_code"],
        assigningAuthorityName="OUH",
    )
    SubElement(custodian_organization, "name").text = location["display_name"]


def _append_component1_encounter(encounter: dict, root: Element) -> None:
    #
    # 				// Set Encounter Information
    # 				EncompassingEncounter encompassingEncounter = this.cdaFactory.createEncompassingEncounter();
    # 				CE encounterCode = this.datatypesFactory.createCE(encounterModel.getEncounterId(), "PAS");
    # 				encompassingEncounter.setCode(encounterCode);
    #
    # 				IVL_TS admissionDate = this.datatypesFactory.createIVL_TS(DATETIME_FORMAT.format(encounterModel.getAdmissionDate()));
    # 				encompassingEncounter.setEffectiveTime(admissionDate);
    #
    # 				Component1 componentOf = this.cdaFactory.createComponent1();
    # 				componentOf.setEncompassingEncounter(encompassingEncounter);
    # 				ccdDocument.setComponentOf(componentOf);
    component1 = SubElement(root, "componentOf", typeCode="COMP")
    # realmCode
    # typeId
    encompassing_encounter = SubElement(
        component1, "encompassingEncounter", classCode="ENC", moodCode="EVN"
    )
    SubElement(
        encompassing_encounter,
        "code",
        code=encounter.get("epr_encounter_id", "") or encounter.get("uuid", ""),
        codeSystem="PAS",
    )
    admitted_time = parse_iso8601_to_datetime(encounter["admitted_at"])
    if admitted_time is not None:
        SubElement(
            encompassing_encounter,
            "effectiveTime",
            value=admitted_time.strftime(DATETIME_FORMAT),
            operator="I",
        )


def _append_component2_pdf_document(
    pdf_file_path: PurePath, data: dict, root: Element
) -> None:
    #
    # 				ED pdfUNCPath = this.datatypesFactory.createED(pdfFile.getAbsolutePath());
    # 				pdfUNCPath.setMediaType(MimeConstants.MIME_PDF);
    # 				pdfUNCPath.setRepresentation(BinaryDataEncoding.TXT);
    #
    # 				NonXMLBody nonXmlBody = this.cdaFactory.createNonXMLBody();
    # 				nonXmlBody.setText(pdfUNCPath);
    #
    # 				Component2 component = this.cdaFactory.createComponent2();
    # 				component.setNonXMLBody(nonXmlBody);
    # 				ccdDocument.setComponent(component);
    component2 = SubElement(
        root, "component", typeCode="COMP", contextConductionInd="true"
    )
    non_xml_body = SubElement(
        component2, "nonXMLBody", classCode="DOCBODY", moodCode="EVN"
    )
    pdf_unc_path = SubElement(
        non_xml_body, "text", mediaType="application/pdf", representation="TXT"
    )
    pdf_unc_path.text = str(pdf_file_path)


def _validate_xml(xml: str, parser: object) -> None:
    etree.fromstring(xml, parser)
