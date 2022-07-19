import copy
from typing import Any, Dict, Optional

import pytest
from flask import Flask
from mock import Mock
from pytest_mock import MockFixture
from requests_mock import Mocker

import dhos_pdf_api.blueprint_api.hl7_cda


@pytest.mark.freeze_time("2019-01-26T10:01:10.000Z")
@pytest.mark.parametrize("date_of_birth", ["1985-07-01", None])
def test_create_cda_xml(
    sample_send_data: Dict, date_of_birth: Optional[str], app: Flask
) -> None:
    parser = app.config["CDA_XML_SCHEMA_PARSER"]
    if date_of_birth is None:
        date_of_birth = ""
        expected_dob = ""
    else:
        date_of_birth = date_of_birth.replace("-", "")
        expected_dob = '        <birthTime value="19850701"/>\n'

    expected = (
        '<?xml version="1.0" ?>\n'
        '<ClinicalDocument xmlns="urn:hl7-org:v3" classCode="DOCCLIN" moodCode="EVN">\n'
        '  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>\n'
        '  <id assigningAuthorityName="PAS" extension="2018L73782250" root="2.16.840.1.113883.4"/>\n'
        '  <code code="pdf-cda-news2-chart" codeSystem="OCI" codeSystemName="Case Notes" displayName="NEWS2 Chart"/>\n'
        '  <title mediaType="text/plain" representation="TXT">NEWS2 Chart</title>\n'
        '  <effectiveTime value="20190126100110"/>\n'
        "  <confidentialityCode/>\n"
        '  <recordTarget contextControlCode="OP" typeCode="RCT">\n'
        '    <patientRole classCode="PAT">\n'
        '      <id assigningAuthorityName="NHS" extension="9991677789" root="2.16.840.1.113883.2.1.4.1"/>\n'
        '      <id assigningAuthorityName="PAS" extension="27988932" root="2.16.840.1.113883.4"/>\n'
        '      <patient classCode="PSN" determinerCode="INSTANCE">\n'
        "        <name>\n"
        '          <given mediaType="text/plain" partType="GIV" representation="TXT">Michele</given>\n'
        '          <family mediaType="text/plain" partType="FAM" representation="TXT">Haynes</family>\n'
        "        </name>\n"
        '        <administrativeGenderCode code="F" codeSystem="2.16.840.1.113883.2.1.3.2.4.16.25"/>\n'
        f"{expected_dob}"
        "      </patient>\n"
        "    </patientRole>\n"
        "  </recordTarget>\n"
        '  <author contextControlCode="OP" typeCode="AUT">\n'
        '    <time value="20190227181515"/>\n'
        '    <assignedAuthor classCode="ASSIGNED">\n'
        '      <id assigningAuthorityName="SEND" extension="G" root="2.16.840.1.113883.4"/>\n'
        '      <assignedPerson classCode="PSN" determinerCode="INSTANCE">\n'
        "        <name>\n"
        '          <given mediaType="text/plain" partType="GIV" representation="TXT">Stan</given>\n'
        '          <family mediaType="text/plain" partType="FAM" representation="TXT">Lee</family>\n'
        "        </name>\n"
        "      </assignedPerson>\n"
        "    </assignedAuthor>\n"
        "  </author>\n"
        '  <custodian typeCode="CST">\n'
        '    <assignedCustodian classCode="ASSIGNED">\n'
        '      <representedCustodianOrganization classCode="ORG" determinerCode="INSTANCE">\n'
        '        <id assigningAuthorityName="OUH" extension="123HO" root="2.16.840.1.113883.4"/>\n'
        "        <name>Birch Hospital</name>\n"
        "      </representedCustodianOrganization>\n"
        "    </assignedCustodian>\n"
        "  </custodian>\n"
        '  <componentOf typeCode="COMP">\n'
        '    <encompassingEncounter classCode="ENC" moodCode="EVN">\n'
        '      <code code="2018L73782250" codeSystem="PAS"/>\n'
        '      <effectiveTime operator="I" value="20190125000000"/>\n'
        "    </encompassingEncounter>\n"
        "  </componentOf>\n"
        '  <component contextConductionInd="true" typeCode="COMP">\n'
        '    <nonXMLBody classCode="DOCBODY" moodCode="EVN">\n'
        '      <text mediaType="application/pdf" representation="TXT">\\\\server\\share\\folder\\2018L73782250.pdf</text>\n'
        "    </nonXMLBody>\n"
        "  </component>\n"
        "</ClinicalDocument>\n"
    )

    xml_data = copy.deepcopy(sample_send_data)
    response = dhos_pdf_api.blueprint_api.hl7_cda.create_hl7_cda_xml(
        xml_data, "//server/share/folder", "2018L73782250.pdf", parser
    )
    # Canonicalize the XML otherwise attribute ordering will break the comparison.
    from lxml.etree import canonicalize

    canonical_output = canonicalize(
        response.decode("utf8"), rewrite_prefixes=True, strip_text=True
    )
    canonical_expected = canonicalize(expected, rewrite_prefixes=True, strip_text=True)
    assert canonical_output == canonical_expected


@pytest.mark.parametrize(
    ["cda_path", "publish_count"], [("//srv/shr/fldr", 1), (None, 0)]
)
def test_pdf_generation_publishes_cda(
    mocker: MockFixture,
    mock_publish_msg: Mock,
    app: Flask,
    sample_send_data: Dict,
    mock_trustomer_config: Dict,
    requests_mock: Mocker,
    cda_path: Optional[str],
    publish_count: Optional[int],
) -> None:
    mocker.patch.object(dhos_pdf_api.blueprint_api.hl7_cda, "create_hl7_cda_xml")
    mocker.patch.dict(app.config, {"SEND_BCP_CDA_UNC_PATH": cda_path})
    mocker.patch.object(dhos_pdf_api.blueprint_api.controller, "write_file")
    mocker.patch("os.path.isdir", return_value=False)
    mocker.patch("os.mkdir")

    mock_post: Any = requests_mock.post(
        f"http://localhost:3000/dhos/v1/send_pdf",
        headers={"Content-Type": "application/pdf"},
        content=b"something",
        status_code=200,
    )

    xml_data = copy.deepcopy(sample_send_data)
    xml_data["pdf_filename"] = "2018L73782250.pdf"
    xml_data["encounter_id"] = "2018L73782250"

    dhos_pdf_api.blueprint_api.controller.create_send_documents(xml_data)
    assert mock_post.called is True
    assert mock_publish_msg.call_count == publish_count
    if publish_count != 0:
        assert mock_publish_msg.call_args[1]["body"]["content"].startswith(
            "<?xml version='1.0'"
        )
