import json
from pathlib import Path
from time import sleep
from typing import Any, List, Tuple
from uuid import uuid4

import pytest
from flask_batteries_included.helpers import generate_uuid
from werkzeug import Client

from dhos_pdf_api.blueprint_api import send_ward_report
from dhos_pdf_api.blueprint_api.controller import generate_send_ward_report_pdf
from dhos_pdf_api.blueprint_api.send_ward_report import SendWardReportWriter


@pytest.mark.usefixtures("app")
class TestSendWardReport:

    hospital_name = "Birch Hospital"
    ward_name = "Dumbledore Ward"
    report_month = "March"
    report_year = "2019"
    draw_methods: List[str] = [
        "draw_pie_chart_text",
        "draw_pie_chart",
        "draw_pie_chart_legend",
        "draw_pie_chart_summary",
        "draw_time_series_text",
        "draw_time_series_percentages",
        "draw_time_series_legend",
        "draw_bar_chart_header",
        "draw_bar_chart",
        "draw_bar_chart_text",
        "draw_vital_signs_recording",
    ]

    @pytest.fixture
    def location_uuid(self) -> str:
        return str(uuid4())

    @pytest.fixture
    def output_pdf_filename(self, location_uuid: str) -> str:
        return f"{location_uuid}.pdf"

    @pytest.fixture
    def pdf_path(self, pdf_output_path: Path, output_pdf_filename: Path) -> Path:
        return pdf_output_path / output_pdf_filename

    @pytest.fixture
    def writer(self, location_uuid: str, pdf_path: Path) -> SendWardReportWriter:
        data_frame = json.loads(
            Path(
                "tests/sample_data/send_ward_report/sample_metric_data.json"
            ).read_text()
        )

        return send_ward_report.SendWardReportWriter(
            pdf_data=data_frame["pdf_data"],
            hospital_name=self.hospital_name,
            ward_name=self.ward_name,
            report_month=self.report_month,
            report_year=self.report_year,
            location_uuid=location_uuid,
            file_path=pdf_path,
        )

    @pytest.mark.parametrize("draw_method", draw_methods)
    def test_all_pdf_elements_are_drawn(
        self, writer: SendWardReportWriter, draw_method: str, mocker: Any
    ) -> None:
        mock_draw = mocker.patch.object(writer, draw_method)
        writer.write()
        assert mock_draw.call_count == 1

    def test_file_name_is_correct(
        self, writer: SendWardReportWriter, output_pdf_filename: str
    ) -> None:
        assert writer.file_name == output_pdf_filename

    def test_file_path_is_correct(
        self, writer: SendWardReportWriter, pdf_path: Path
    ) -> None:
        assert writer.file_path == pdf_path

    def test_retrieve_pdf(self, writer: SendWardReportWriter, pdf_path: Path) -> None:
        writer.write()
        reader = send_ward_report.SendWardReportReader(file_path=pdf_path)
        content = reader.read()
        assert isinstance(content, bytes)

    def test_post_endpoint(self, client: Client, mock_bearer_validation: Any) -> None:
        with open(
            Path("tests/sample_data/send_ward_report/sample_metric_data.json"), "r"
        ) as json_file:
            post_data = json.loads(json_file.read())

        response = client.post(
            "/dhos/v1/ward_report",
            json=post_data,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 201, response.json

    def test_get_endpoint(
        self,
        client: Client,
        writer: SendWardReportWriter,
        location_uuid: str,
        mock_bearer_validation: Any,
    ) -> None:
        writer.write()
        response = client.get(
            f"/dhos/v1/ward_report/{location_uuid}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200, response.json

    @pytest.fixture
    def writer_with_zeroes(
        self, location_uuid: str, pdf_path: Path
    ) -> SendWardReportWriter:
        with open(
            Path(
                "tests/sample_data/send_ward_report/sample_metric_data_with_zeroes.json"
            ),
            "r",
        ) as pdf_file:
            data_frame = json.loads(pdf_file.read())
        return send_ward_report.SendWardReportWriter(
            pdf_data=data_frame["pdf_data"],
            hospital_name=self.hospital_name,
            ward_name=self.ward_name,
            report_month=self.report_month,
            report_year=self.report_year,
            location_uuid=location_uuid,
            file_path=pdf_path,
        )

    @pytest.mark.parametrize("draw_method", draw_methods)
    def test_all_pdf_elements_are_drawn_with_zero_obs(
        self, writer_with_zeroes: SendWardReportWriter, draw_method: str, mocker: Any
    ) -> None:
        mock_draw = mocker.patch.object(writer_with_zeroes, draw_method)
        writer_with_zeroes.write()
        assert mock_draw.call_count == 1

    def test_file_name_is_correct_with_zero_obs(
        self, writer_with_zeroes: SendWardReportWriter, output_pdf_filename: str
    ) -> None:
        assert writer_with_zeroes.file_name == output_pdf_filename

    def test_file_path_is_correct_with_zero_obs(
        self, writer_with_zeroes: SendWardReportWriter, pdf_path: str
    ) -> None:
        assert writer_with_zeroes.file_path == pdf_path

    def test_retrieve_pdf_with_zero_obs(
        self, writer_with_zeroes: SendWardReportWriter, pdf_path: Path
    ) -> None:
        writer_with_zeroes.write()
        reader = send_ward_report.SendWardReportReader(file_path=pdf_path)
        content = reader.read()
        assert isinstance(content, bytes)

    def test_many_threads(self, pdf_output_path: Path) -> None:
        from multiprocessing.pool import ThreadPool

        n_threads = 2
        n_pdfs = 5
        pool = ThreadPool(processes=n_threads)

        results = pool.map(
            threaded_writer, [(f"Ward {d}", pdf_output_path, d) for d in range(n_pdfs)]
        )
        assert len(results) == n_pdfs


def threaded_writer(args: Tuple[str, Path, int]) -> str:
    ward_name, output_folder, index = args
    sleep(index / 10)
    location_uuid = generate_uuid()
    data_frame = json.loads(
        Path("tests/sample_data/send_ward_report/sample_metric_data.json").read_text()
    )
    generate_send_ward_report_pdf(
        {
            "pdf_data": data_frame["pdf_data"],
            "hospital_name": "Birch Hospital",
            "ward_name": ward_name,
            "report_month": "March",
            "report_year": "2019",
            "location_uuid": location_uuid,
        },
        ward_report_folder=output_folder,
    )
    return location_uuid
