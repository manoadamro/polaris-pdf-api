import uuid
from typing import Dict

import requests
from cachetools import TTLCache, cached
from flask import current_app
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from she_logging import logger
from she_logging.request_id import current_request_id

from dhos_pdf_api import config


def get_trustomer_base_url() -> str:
    return current_app.config["DHOS_TRUSTOMER_API_HOST"]


_cache: TTLCache = TTLCache(1, config.Configuration().TRUSTOMER_CONFIG_CACHE_TTL_SEC)


@cached(cache=_cache)  # cache for 1 hour
def get_trustomer_config() -> Dict:
    customer_code = current_app.config["CUSTOMER_CODE"].lower()
    url = f"{get_trustomer_base_url()}/dhos/v1/trustomer/{customer_code}"
    logger.info("Fetching trustomer config from %s", url)
    try:
        response = requests.get(
            url=url,
            headers={
                "X-Request-ID": current_request_id() or str(uuid.uuid4()),
                "Authorization": current_app.config["POLARIS_API_KEY"],
                "X-Trustomer": customer_code,
                "X-Product": "polaris",
            },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.exception("Failed to get trustomer config")
        raise ServiceUnavailableException(e)
    return response.json()
