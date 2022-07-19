from pathlib import Path

import connexion
import kombu_batteries_included
from connexion import FlaskApp
from flask import Flask
from flask_batteries_included import augment_app as fbi_augment_app
from flask_batteries_included.config import is_not_production_environment
from flask_batteries_included.sqldb import db, init_db
from she_logging import logger

from dhos_pdf_api.blueprint_api import api_blueprint
from dhos_pdf_api.config import init_config
from dhos_pdf_api.helper.cli import add_cli_command


def create_app(
    testing: bool = False, use_pgsql: bool = True, use_sqlite: bool = False
) -> Flask:
    openapi_dir: Path = Path(__file__).parent / "openapi"
    connexion_app: FlaskApp = connexion.App(
        __name__,
        specification_dir=openapi_dir,
        options={"swagger_ui": is_not_production_environment()},
    )
    connexion_app.add_api("openapi.yaml", strict_validation=True)

    # Create a Flask app.
    app: Flask = fbi_augment_app(
        app=connexion_app.app,
        use_pgsql=use_pgsql,
        use_sqlite=use_sqlite,
        use_auth0=True,
        testing=testing,
    )

    init_config(app)

    # Initialise k-b-i library to allow publishing to RabbitMQ.
    kombu_batteries_included.init()

    # Register the API blueprint.
    app.register_blueprint(api_blueprint, url_prefix="/dhos/v1")
    app.logger.info("Registered API blueprint")

    # Configure the SQL database
    init_db(app=app, testing=testing)

    # Create all the tables in the in-memory database
    if testing:
        with app.app_context():
            db.create_all()

    add_cli_command(app)

    # Create directories we need if they don't already exist
    for key in (
        "SEND_BCP_OUTPUT_DIR",
        "SEND_BCP_RSYNC_DIR",
        "SEND_DISCHARGE_OUTPUT_DIR",
        "SEND_TMP_OUTPUT_DIR",
        "SEND_WARD_REPORT_OUTPUT_DIR",
    ):
        if app.config[key]:
            path: Path = Path(app.config[key])
            path.mkdir(parents=True, exist_ok=True)

    # Done!
    logger.info("App ready to serve requests")

    return app
