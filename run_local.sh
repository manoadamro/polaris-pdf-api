#!/bin/bash
SERVER_PORT=${1-5000}
export SERVER_PORT=${SERVER_PORT}
export ENVIRONMENT=DEVELOPMENT
export EXTERNAL_URL=http://localhost:${SERVER_PORT}
export SERVER_TIMEZONE=UTC
export FLASK_APP=dhos_pdf_api/autoapp.py
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=dhos-pdf-api
export DATABASE_PASSWORD=dhos-pdf-api
export DATABASE_NAME=dhos-pdf-api
export AUTH0_DOMAIN=https://login-sandbox.sensynehealth.com/
export AUTH0_AUDIENCE=https://dev.sensynehealth.com/
export AUTH0_METADATA=https://gdm.sensynehealth.com/metadata
export AUTH0_JWKS_URL=https://login-sandbox.sensynehealth.com/.well-known/jwks.json
export DHOS_PDF_ENGINE_URL=http://localhost:3000
export GDM_BCP_OUTPUT_DIR=gdm-bcp-output
export DBM_BCP_OUTPUT_DIR=dbm-bcp-output
export SEND_BCP_OUTPUT_DIR=send-bcp-output
export SEND_DISCHARGE_OUTPUT_DIR=send-discharge-output
export SEND_WARD_REPORT_OUTPUT_DIR=send-ward-report-output
export SEND_TMP_OUTPUT_DIR=/tmp
export SEND_BCP_RSYNC_DIR=send-bcp-rsync
export PROXY_URL=http://localhost
export HS_KEY=secret
export REDIS_INSTALLED=False
export IGNORE_JWT_VALIDATION=true
export RABBITMQ_DISABLED=true
export DHOS_TRUSTOMER_API_HOST=http://dhos-trustomer
export CUSTOMER_CODE=dev
export POLARIS_API_KEY=secret
export LOG_LEVEL=${LOG_LEVEL:-DEBUG}
export LOG_FORMAT=${LOG_FORMAT:-COLOUR}

if [ -z "$*" ]
then
  flask db upgrade
  python -m dhos_pdf_api
else
  flask $*
fi
