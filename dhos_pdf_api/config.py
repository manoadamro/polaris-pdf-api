import os
from typing import Optional

from environs import Env
from flask import Flask
from lxml import etree


def _load_parser() -> object:
    root_path = os.path.dirname(os.path.abspath(__file__))
    xsd = os.path.join(root_path, "schema", "infrastructure", "cda", "CDA_SDTC.xsd")
    with open(xsd, "r") as f:
        schema_doc = etree.parse(f)
        schema = etree.XMLSchema(schema_doc)
        return etree.XMLParser(schema=schema)


class Configuration:
    env = Env()
    DHOS_PDF_ENGINE_URL: str = env.str("DHOS_PDF_ENGINE_URL", "http://localhost:3000")
    SERVER_TIMEZONE: str = env.str("SERVER_TIMEZONE")
    GDM_BCP_OUTPUT_DIR: str = env.str("GDM_BCP_OUTPUT_DIR")
    DBM_BCP_OUTPUT_DIR: str = env.str("DBM_BCP_OUTPUT_DIR")
    SEND_BCP_OUTPUT_DIR: str = env.str("SEND_BCP_OUTPUT_DIR")
    SEND_BCP_RSYNC_DIR: str = env.str("SEND_BCP_RSYNC_DIR")
    # SEND_TMP_OUTPUT_DIR needs to be on the same file system as
    # SEND_DISCHARGE_OUTPUT_DIR to ensure atomic writes
    SEND_DISCHARGE_OUTPUT_DIR: Optional[str] = env.str(
        "SEND_DISCHARGE_OUTPUT_DIR", None
    )
    SEND_TMP_OUTPUT_DIR: str = env.str("SEND_TMP_OUTPUT_DIR")
    SEND_BCP_CDA_UNC_PATH: Optional[str] = env.str("SEND_BCP_CDA_UNC_PATH", None)
    SEND_WARD_REPORT_OUTPUT_DIR: str = env.str("SEND_WARD_REPORT_OUTPUT_DIR")
    CDA_XML_SCHEMA_PARSER: object = _load_parser()
    CUSTOMER_CODE: str = env.str("CUSTOMER_CODE")
    DHOS_TRUSTOMER_API_HOST: str = env.str("DHOS_TRUSTOMER_API_HOST")
    POLARIS_API_KEY: str = env.str("POLARIS_API_KEY")
    TRUSTOMER_CONFIG_CACHE_TTL_SEC: int = env.int(
        "TRUSTOMER_CONFIG_CACHE_TTL_SEC", 60 * 60  # Cache for 1 hour by default.
    )


def init_config(app: Flask) -> None:
    app.config.from_object(Configuration)
