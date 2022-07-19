FROM python:3.9-slim

ARG GEMFURY_DOWNLOAD_KEY
ENV FLASK_APP dhos_pdf_api/autoapp.py

WORKDIR /app

RUN apt-get update \
    && apt-get -y install wget xz-utils fontconfig postgresql-client openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev \
    && mkdir /install \
    && cd /install \
    && wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
    && tar xvf wkhtmltox*.tar.xz \
    && mv wkhtmltox/bin/wkhtmlto* /usr/bin \
    && rm -rf /install \
    && mkdir -p /usr/share/fonts/truetype/noto
    
COPY dhos_pdf_api/fonts/* /usr/share/fonts/truetype/
    
COPY poetry.lock pyproject.toml ./

RUN apt-get update \
    && apt-get install -y wait-for-it curl nano \
    && useradd -m app \
    && chown -R app:app /app \
    && pip install --upgrade pip poetry \
    && poetry config http-basic.sensynehealth ${GEMFURY_DOWNLOAD_KEY:?Missing build argument} '' \
    && poetry config virtualenvs.create false \
    && poetry install -v --no-dev \
    && chmod 644 /usr/share/fonts/truetype/* \
    && fc-cache -fv

COPY --chown=app . ./

USER app

EXPOSE 5000

CMD ["python", "-m", "dhos_pdf_api"]
