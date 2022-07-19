import logging
from pathlib import Path
from typing import Any, Dict, List, Type

import numpy as np
import pandas as pd
from flask_batteries_included.helpers.error_handler import EntityNotFoundException
from pandas import Series

# Change matplotlib logging level.
logging.getLogger("matplotlib").setLevel(logging.WARNING)
import matplotlib

matplotlib.use("pdf")
from matplotlib import pyplot as plot
from matplotlib.backends.backend_pdf import PdfPages


class CellStyles:
    @staticmethod
    def hide_splines(obj: Any) -> None:
        obj.axes.spines["top"].set_visible(False)
        obj.axes.spines["right"].set_visible(False)
        obj.axes.spines["bottom"].set_visible(False)
        obj.axes.spines["left"].set_visible(False)

    @staticmethod
    def hide_axes(obj: Any) -> None:
        obj.axes.get_xaxis().set_visible(False)
        obj.axes.get_yaxis().set_visible(False)

    @classmethod
    def hide_all(cls, obj: Any) -> None:
        cls.hide_axes(obj)
        cls.hide_splines(obj)


class AxesStyles:
    @staticmethod
    def hide_legend(obj: Any) -> None:
        obj.legend().set_visible(False)


class SendWardReportData:
    ################################
    #
    # ASSUMPTIONS
    #
    ################################
    """
    data_subset_df (above) is the input to this code section.

    This input is a pd.DataFrame with the headers as follows:

    'metric_values_id',             # potentially not needed for .pdf generation; dtype = int;
                                      counter of rows - useful for Data Engineering book keeping

    'location_type_name',           # not needed for .pdf generation

    'location_type_snomed',         # not needed for .pdf generation

    'location_uuid',                # NEEDED for file storage/retrieval

    'location_id',                  # potentially not needed for .pdf generation; dtype = int;
                                      useful from the perspective of Data Engineering book keeping

    'location_display_name',        # NEEDED for .pdf generation; dtype = str

    'parent_location_id',           # potentially not needed for .pdf generation; dtype = int;
                                      useful from the perspective of Data Engineering book keeping

    'measurement_timestamp',        # NEEDED for .pdf generation; dtype = object??? YYYY-MM-DD

    'metric_value',                 # NEEDED for .pdf generation; dtype = int

    'metric_id',                    # potentially not needed for .pdf generation; dtype = int;
                                      useful from the perspective of Data Engineering book keeping

    'metric_name',                  # NEEDED for .pdf generation; dtype = str

    'metric_description',           # potentially not needed for .pdf generation; dtype = str;
                                      useful from the perspective of Data Engineering book keeping

    'parent_location_display_name', # NEEDED for .pdf generation; dtype = str

    'parent_location_child_location'# NEEDED for .pdf generation; dtype = str

    Note: valid values within metric_name are:

    - count_obs_sets_on_time_high_risk
    - count_obs_sets_on_time_med_risk
    - count_obs_sets_on_time_lomed_risk
    - count_obs_sets_on_time_low_risk
    - count_obs_sets_on_time_zero_risk

    - count_obs_sets_late_high_risk
    - count_obs_sets_late_med_risk
    - count_obs_sets_late_lomed_risk
    - count_obs_sets_late_low_risk
    - count_obs_sets_late_zero_risk

    - count_obs_sets_complete
    - count_obs_sets_partial
    - count_obs_missing_temperature
    - count_obs_missing_spo2
    - count_obs_missing_acvpu
    - count_obs_missing_hr
    - count_obs_missing_rr
    - count_obs_missing_sbp
    - count_obs_missing_o2therapy

    - count_obs_missing_temperature_pat_refused
    - count_obs_missing_spo2_pat_refused
    - count_obs_missing_hr_pat_refused
    - count_obs_missing_rr_pat_refused
    - count_obs_missing_sbp_pat_refused

    i.e. there is a total of 5+5+9+5 = 24 metrics.

    The first 10 metrics are used for producing percentages of obs on time for the time series plot,
    and for the pie chart (after obs sets taken early/ late are summed together).

    The next 9 metrics are used for producing the bar plot at the bottom.

    The last 5 metrics are not used for these plots, but will be important for PMCF.

    Without the first 10+9 = 19 metrics, the code below won't work.
    """

    ################################
    #
    # END OF ASSUMPTIONS
    #
    ################################

    def __init__(self, subset: List, location_uuid: str) -> None:
        """
        computing aggregate metrics for pie chart and bar plot
        """

        formatted_subst = self.report_formatting(subset)

        self.subset = pd.DataFrame.from_dict(formatted_subst)

        self.out_df = self.preprocess()
        self.location_uuid = location_uuid

        self.count_obs_sets_on_time = self.out_df["count_obs_sets_on_time"].sum()
        self.count_obs_sets_late = self.out_df["count_obs_sets_late"].sum()
        self.perc_obs_sets_on_time = self.calculate_percentage_integers(
            self.count_obs_sets_on_time,
            (self.count_obs_sets_on_time + self.count_obs_sets_late),
        )
        self.perc_obs_sets_late = self.calculate_percentage_integers(
            self.count_obs_sets_late,
            (self.count_obs_sets_on_time + self.count_obs_sets_late),
        )
        self.count_obs_sets_complete = self.out_df["count_obs_sets_complete"].sum()
        self.count_obs_sets_partial = self.out_df["count_obs_sets_partial"].sum()
        self.count_obs_missing_temperature = self.out_df[
            "count_obs_missing_temperature"
        ].sum()
        self.count_obs_missing_spo2 = self.out_df["count_obs_missing_spo2"].sum()
        self.count_obs_missing_acvpu = self.out_df["count_obs_missing_acvpu"].sum()
        self.count_obs_missing_hr = self.out_df["count_obs_missing_hr"].sum()
        self.count_obs_missing_rr = self.out_df["count_obs_missing_rr"].sum()
        self.count_obs_missing_sbp = self.out_df["count_obs_missing_sbp"].sum()
        self.count_obs_missing_o2therapy = self.out_df[
            "count_obs_missing_o2therapy"
        ].sum()
        self.perc_obs_sets_complete = self.calculate_percentage_integers(
            (self.out_df["count_obs_sets_complete"].sum()),
            (
                (
                    self.out_df["count_obs_sets_complete"]
                    + self.out_df["count_obs_sets_partial"]
                ).sum()
            ),
        )

    def locate(self, metric_name: str) -> Any:
        return self.subset.loc[self.subset["metric_name"] == metric_name]

    def output(self, metric_name: str) -> pd.DataFrame:
        """
        Function that takes a pandas.DataFrame and metric_name
        and produces a smaller output DataFrame with just one column (with the metric = metric_name)
        and indexed by timestamp
        """
        out_df = self.locate(metric_name).pivot_table(
            index="metric_date", values="metric_value"
        )
        out_df.columns = [metric_name]
        return out_df

    def report_formatting(self, pdf_data: list) -> Dict:
        report_format: dict = {
            "measurement_timestamp": [],
            "metric_value": [],
            "metric_name": [],
            "metric_date": [],
        }
        for metric in pdf_data:
            for metric_key, metric_value in metric.items():
                if metric_key == "metric_value":
                    report_format[metric_key].append(int(metric_value))
                else:
                    report_format[metric_key].append(metric_value)
        return report_format

    def preprocess(self) -> pd.DataFrame:
        """
        extracting relevant data from the input dataframe (self.subset)
        """
        # on time
        out_df = self.output(metric_name="count_obs_sets_on_time_high_risk")
        out_df["count_obs_sets_on_time_med_risk"] = self.output(
            metric_name="count_obs_sets_on_time_med_risk"
        )
        out_df["count_obs_sets_on_time_lomed_risk"] = self.output(
            metric_name="count_obs_sets_on_time_lomed_risk"
        )
        out_df["count_obs_sets_on_time_low_risk"] = self.output(
            metric_name="count_obs_sets_on_time_low_risk"
        )
        out_df["count_obs_sets_on_time_zero_risk"] = self.output(
            metric_name="count_obs_sets_on_time_zero_risk"
        )
        # late
        out_df["count_obs_sets_late_high_risk"] = self.output(
            metric_name="count_obs_sets_late_high_risk"
        )
        out_df["count_obs_sets_late_med_risk"] = self.output(
            metric_name="count_obs_sets_late_med_risk"
        )
        out_df["count_obs_sets_late_lomed_risk"] = self.output(
            metric_name="count_obs_sets_late_lomed_risk"
        )
        out_df["count_obs_sets_late_low_risk"] = self.output(
            metric_name="count_obs_sets_late_low_risk"
        )
        out_df["count_obs_sets_late_zero_risk"] = self.output(
            metric_name="count_obs_sets_late_zero_risk"
        )
        # partial/complete
        out_df["count_obs_sets_complete"] = self.output(
            metric_name="count_obs_sets_complete"
        )
        out_df["count_obs_sets_partial"] = self.output(
            metric_name="count_obs_sets_partial"
        )
        # missing
        out_df["count_obs_missing_temperature"] = self.output(
            metric_name="count_obs_missing_temperature"
        )
        out_df["count_obs_missing_spo2"] = self.output(
            metric_name="count_obs_missing_spo2"
        )
        out_df["count_obs_missing_acvpu"] = self.output(
            metric_name="count_obs_missing_acvpu"
        )
        out_df["count_obs_missing_hr"] = self.output(metric_name="count_obs_missing_hr")
        out_df["count_obs_missing_rr"] = self.output(metric_name="count_obs_missing_rr")
        out_df["count_obs_missing_sbp"] = self.output(
            metric_name="count_obs_missing_sbp"
        )
        out_df["count_obs_missing_o2therapy"] = self.output(
            metric_name="count_obs_missing_o2therapy"
        )
        # computing derived metrics - perc obs sets taken on time are used for time series plot
        out_df["count_obs_sets_on_time"] = (
            out_df["count_obs_sets_on_time_high_risk"]
            + out_df["count_obs_sets_on_time_med_risk"]
            + out_df["count_obs_sets_on_time_lomed_risk"]
            + out_df["count_obs_sets_on_time_low_risk"]
            + out_df["count_obs_sets_on_time_zero_risk"]
        )
        out_df["count_obs_sets_late"] = (
            out_df["count_obs_sets_late_high_risk"]
            + out_df["count_obs_sets_late_med_risk"]
            + out_df["count_obs_sets_late_lomed_risk"]
            + out_df["count_obs_sets_late_low_risk"]
            + out_df["count_obs_sets_late_zero_risk"]
        )
        out_df["count_obs_sets_high_risk"] = (
            out_df["count_obs_sets_on_time_high_risk"]
            + out_df["count_obs_sets_late_high_risk"]
        )
        out_df["count_obs_sets_med_risk"] = (
            out_df["count_obs_sets_on_time_med_risk"]
            + out_df["count_obs_sets_late_med_risk"]
        )
        out_df["count_obs_sets_lomed_risk"] = (
            out_df["count_obs_sets_on_time_lomed_risk"]
            + out_df["count_obs_sets_late_lomed_risk"]
        )
        out_df["count_obs_sets_low_risk"] = (
            out_df["count_obs_sets_on_time_low_risk"]
            + out_df["count_obs_sets_late_low_risk"]
        )
        out_df["count_obs_sets_zero_risk"] = (
            out_df["count_obs_sets_on_time_zero_risk"]
            + out_df["count_obs_sets_late_zero_risk"]
        )
        out_df["count_obs_sets"] = (
            out_df["count_obs_sets_on_time"] + out_df["count_obs_sets_late"]
        )
        out_df["perc_obs_sets_on_time_high_risk"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time_high_risk"],
            out_df["count_obs_sets_high_risk"],
        )
        out_df["perc_obs_sets_on_time_med_risk"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time_med_risk"], out_df["count_obs_sets_med_risk"]
        )
        out_df["perc_obs_sets_on_time_lomed_risk"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time_lomed_risk"],
            out_df["count_obs_sets_lomed_risk"],
        )
        out_df["perc_obs_sets_on_time_low_risk"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time_low_risk"], out_df["count_obs_sets_low_risk"]
        )
        out_df["perc_obs_sets_on_time_zero_risk"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time_zero_risk"],
            out_df["count_obs_sets_zero_risk"],
        )
        out_df["perc_obs_sets_on_time"] = self.calculate_percentage_series(
            out_df["count_obs_sets_on_time"], out_df["count_obs_sets"]
        )
        out_df["perc_obs_sets_complete"] = self.calculate_percentage_series(
            out_df["count_obs_sets_complete"],
            (out_df["count_obs_sets_complete"] + out_df["count_obs_sets_partial"]),
        )

        return out_df

    def calculate_percentage_series(self, a: float, b: float) -> Series:
        perc_column = pd.Series(100 * (a / b))
        perc_column.fillna(0, inplace=True)
        return perc_column

    def calculate_percentage_integers(self, a: int, b: int) -> float:
        if b == 0:
            return 0
        return 100 * (a / b)


class SendWardReportIO:
    def __init__(self, file_path: Path) -> None:
        self.file_name = file_path.name
        self.file_path = file_path


class SendWardReportWriter(SendWardReportIO):
    def __init__(
        self,
        pdf_data: list,
        hospital_name: str,
        ward_name: str,
        report_month: str,
        report_year: str,
        location_uuid: str,
        file_path: Path,
    ):
        self.data: SendWardReportData = SendWardReportData(pdf_data, location_uuid)

        self.hospital_name_ward_name = " ".join((hospital_name, ward_name))
        self.month_year = " ".join((report_month, report_year))

        # post set
        self.pdf_pages: Any = None
        self.grid_size: Any = None
        self.fig: Any = None

        super(SendWardReportWriter, self).__init__(file_path)

    def __enter__(
        self,
    ) -> "SendWardReportWriter":  # has to be string since type does not exist yet
        self.pdf_pages = PdfPages(self.file_path)
        self.grid_size = (25, 5)
        self.fig = plot.figure(figsize=(8.27, 11.69), dpi=100)
        return self

    def __exit__(
        self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Any
    ) -> None:
        self.pdf_pages.savefig(self.fig)
        self.pdf_pages.close()
        plot.close("all")

    def draw_pie_chart_text(self) -> None:
        """
        text above pie chart
        """
        # takes up the first (0th) row, starts in column 0, stretches across 5 columns
        plot.subplot2grid(self.grid_size, (0, 0), colspan=5)
        plot.text(x=0, y=3.0, s=self.hospital_name_ward_name, fontsize=13)
        plot.text(x=0, y=2.15, s=self.month_year, fontsize=13)
        plot.text(x=0, y=1.0, s="Overall Performance", fontsize=11)
        plot.text(x=0, y=0.45, s="All observation sets taken on time", fontsize=8)
        plot.text(x=0, y=0.00, s="or late in the specified month", fontsize=8)
        # hiding both axes and the graph frame (spines)
        CellStyles.hide_all(plot.gca())

    def draw_pie_chart(self) -> None:
        """
        Pie chart
        """
        x: List[float] = []
        colors: List[str] = []
        labels: List[float] = []
        if self.data.count_obs_sets_late > 0:
            x.append(self.data.count_obs_sets_late)
            colors.append("#B4464D")
            labels.append(self.data.count_obs_sets_late)

        if self.data.count_obs_sets_on_time > 0:
            x.append(self.data.count_obs_sets_on_time)
            colors.append("#46B4AD")
            labels.append(self.data.count_obs_sets_on_time)

        plot.subplot2grid(self.grid_size, (1, 0), colspan=2, rowspan=4)
        plot.pie(
            x=x,
            startangle=-270,
            colors=colors,
            labels=labels,
            textprops={"size": 8},
            normalize=True,
        )

    def draw_pie_chart_legend(self) -> None:
        """
        Legend below Pie chart
        """
        # (Not handled as legend() in Python because I wanted more control over what I display)
        pie_labels = [
            "Observation sets taken late",
            "Observation sets taken on time",
        ]  # careful, don't change the order of pie_labels
        plot.subplot2grid(self.grid_size, (5, 0), colspan=2)
        plot.text(
            x=0, y=-0.3, s="\u25a0", fontsize=14, color="#B4464D"
        )  # print red square
        plot.text(
            x=0.10,
            y=-0.3,
            s=f"{pie_labels[0]}: {str(int(round(self.data.perc_obs_sets_late)))}%",
            fontsize=8,
        )
        plot.text(
            x=0, y=0.4, s="\u25a0", fontsize=14, color="#46B4AD"
        )  # print green square
        plot.text(
            x=0.10,
            y=0.4,
            s=f"{pie_labels[1]}: {str(int(round(self.data.perc_obs_sets_on_time)))}%",
            fontsize=8,
        )
        # hiding both axes and the graph frame (spines)
        CellStyles.hide_all(plot.gca())

    def draw_pie_chart_summary(self) -> None:
        """
        Text to the RHS of pie chart
        """
        plot.subplot2grid(self.grid_size, (1, 2), colspan=3, rowspan=4)
        plot.text(x=0.05, y=0.75, s="Summary", fontsize=11)
        plot.text(
            x=0.05,
            y=0.55,
            s=f"{str(int(round(self.data.perc_obs_sets_on_time)))}%",
            fontsize=8,
        )
        plot.text(
            x=0.15,
            y=0.55,
            s="of the ward's observation sets were taken on time",
            fontsize=8,
        )
        plot.text(x=0.15, y=0.45, s="or early in the specified month.", fontsize=8)
        plot.text(
            x=0.05,
            y=0.25,
            s=f"{str(int(round(self.data.perc_obs_sets_late)))}%",
            fontsize=8,
        )
        plot.text(
            x=0.15,
            y=0.25,
            s="of the ward's observation sets were taken late",
            fontsize=8,
        )
        plot.text(x=0.15, y=0.15, s="in the specified month.", fontsize=8)
        # hiding both axes but leaving the box around the text
        CellStyles.hide_axes(plot.gca())

    def draw_time_series_text(self) -> None:
        """
        Text above timeseries
        """
        plot.subplot2grid(self.grid_size, (7, 0), colspan=5)
        plot.text(
            x=0,
            y=0.2,
            s="Percentage of all observation sets taken on time in the specified month",
            fontsize=11,
        )
        # hiding both axes and the graph frame (spines)
        CellStyles.hide_all(plot.gca())

    def draw_time_series_percentages(self) -> None:
        """
        Timeseries - percentage of obs sets completed on time by risk category
        """
        ax = plot.subplot2grid(self.grid_size, (8, 0), colspan=5, rowspan=5)
        # selecting data to plot
        data_to_plot = self.data.out_df.loc[
            :,
            [
                "perc_obs_sets_on_time_high_risk",
                "perc_obs_sets_on_time_med_risk",
                "perc_obs_sets_on_time_lomed_risk",
                "perc_obs_sets_on_time_low_risk",
                "perc_obs_sets_on_time_zero_risk",
                "perc_obs_sets_on_time",
            ],
        ]
        plot.axhline(y=90, color="grey", linestyle="--")  # target line
        data_to_plot.index = pd.to_datetime(
            data_to_plot.index
        )  # python datetime functions expect datetime objects
        # default index is "YYYY-MM-DD", we are changing this to be "MMM dd, day"
        data_to_plot = data_to_plot.assign(
            formatted_date=[
                f"{elem.strftime('%b %d')}, {elem.day_name()[0:3]}"
                for elem in data_to_plot.index
            ]
        )
        data_to_plot.set_index(
            "formatted_date", inplace=True
        )  # need to reindex before plotting
        data_to_plot.plot(
            ax=ax,
            color=["#C85200", "#FC7D0A", "#FFBC79", "#A3CCE9", "#1070AA", "#57606C"],
            marker="o",
            markersize=5,
        )
        # sorting out tick labels to be Month-day, day name
        ax.set_xticks(
            np.linspace(0, len(data_to_plot.index) - 1, len(data_to_plot.index))
        )
        ax.tick_params(axis="both", which="major", labelsize=8)
        ax.tick_params(axis="both", which="minor", labelsize=8)
        ax.set_xticklabels(data_to_plot.index, rotation=90)
        ax.set_ylim(-0.05, 105.5)
        ax.set_xlabel("")  # hiding x axis label
        AxesStyles.hide_legend(ax)

    def draw_time_series_legend(self) -> None:
        """
        legend below timeseries
        """
        plot.subplot2grid(self.grid_size, (16, 2), colspan=2, rowspan=2)
        plot.text(
            x=0.32, y=1.15, s="\u25a0", fontsize=14, color="#A3CCE9"
        )  # print square
        plot.text(
            x=0.42, y=1.15, s="Low-risk observation sets taken on time", fontsize=8
        )
        plot.text(
            x=0.32, y=0.85, s="\u25a0", fontsize=14, color="#1070AA"
        )  # print square
        plot.text(
            x=0.42, y=0.85, s="Zero-risk observation sets taken on time", fontsize=8
        )
        plot.text(
            x=0.32, y=0.55, s="\u25a0", fontsize=14, color="#57606C"
        )  # print square
        plot.text(x=0.42, y=0.55, s="All observation sets taken on time", fontsize=8)
        plot.text(
            x=0.32, y=0.25, s="--", fontsize=14, color="grey"
        )  # print target line
        plot.text(
            x=0.42, y=0.25, s="Target: 90% of observation sets on time", fontsize=8
        )
        # hiding both axes and the graph frame (spines)
        CellStyles.hide_all(plot.gca())

        plot.subplot2grid(self.grid_size, (16, 0), colspan=2, rowspan=2)
        plot.text(x=0, y=1.15, s="\u25a0", fontsize=14, color="#C85200")  # print square
        plot.text(
            x=0.1, y=1.15, s="High-risk observation sets taken on time", fontsize=8
        )
        plot.text(x=0, y=0.85, s="\u25a0", fontsize=14, color="#FC7D0A")  # print square
        plot.text(
            x=0.1, y=0.85, s="Medium-risk observation sets taken on time", fontsize=8
        )
        plot.text(x=0, y=0.55, s="\u25a0", fontsize=14, color="#FFBC79")  # print square
        plot.text(
            x=0.1,
            y=0.55,
            s="Low-medium-risk observation sets taken on time",
            fontsize=8,
        )
        CellStyles.hide_all(plot.gca())

    def draw_bar_chart_header(self) -> None:
        """
        bar chart header
        """
        plot.subplot2grid(self.grid_size, (18, 2), colspan=3, rowspan=1)
        plot.text(x=0, y=0.2, s="Missing Vital Signs", fontsize=11)
        CellStyles.hide_all(plot.gca())

    def draw_bar_chart(self) -> None:
        """
        bar chart
        """
        # TODO make gridlines
        plot.subplot2grid(self.grid_size, (19, 2), colspan=3, rowspan=5)
        data_to_plot = [
            self.data.count_obs_missing_acvpu,
            self.data.count_obs_missing_hr,
            self.data.count_obs_missing_spo2,
            self.data.count_obs_missing_o2therapy,
            self.data.count_obs_missing_rr,
            self.data.count_obs_missing_sbp,
            self.data.count_obs_missing_temperature,
        ]
        plot.bar(
            x=[1, 2, 3, 4, 5, 6, 7],
            height=data_to_plot,
            width=0.8,
            color="#46B4AD",
            zorder=3,
        )
        plot.xticks(
            [1, 2, 3, 4, 5, 6, 7],
            (
                "ACVPU",
                "Heart\nRate",
                "O2\nSats",
                "O2\nTherapy",
                "Resp.\nRate",
                "Systolic\nBP",
                "Temp.",
            ),
            rotation=70,
        )
        plot.tick_params(axis="both", which="major", labelsize=8)
        plot.grid(zorder=0, linestyle="--")

    def draw_bar_chart_text(self) -> None:
        """
        text on the LHS of bar chart
        """
        plot.subplot2grid(self.grid_size, (18, 0), colspan=2, rowspan=1)
        plot.text(x=0, y=0.2, s="Vital Signs Recording", fontsize=11)
        CellStyles.hide_all(plot.gca())

    def draw_vital_signs_recording(self) -> None:
        """
        Vital signs recordings
        """
        plot.subplot2grid(self.grid_size, (19, 0), colspan=1, rowspan=2)
        plot.text(
            x=0.25,
            y=0.8,
            s=f"{str(int(round(self.data.perc_obs_sets_complete))) }%",
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=0.8,
            s="of the ward's observation",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=0.55,
            s="sets were complete.",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=0.10,
            s=str(int(round(self.data.count_obs_sets_partial))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=0.10,
            s="observation sets record-",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-0.15,
            s="ded were incomplete.",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-0.4,
            s="Out of these:",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )

        plot.text(
            x=0.25,
            y=-0.8,
            s=str(int(round(self.data.count_obs_missing_acvpu))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-1.05,
            s=str(int(round(self.data.count_obs_missing_hr))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-1.3,
            s=str(int(round(self.data.count_obs_missing_spo2))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-1.55,
            s=str(int(round(self.data.count_obs_missing_o2therapy))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-1.8,
            s=str(int(round(self.data.count_obs_missing_rr))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-2.05,
            s=str(int(round(self.data.count_obs_missing_sbp))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.25,
            y=-2.3,
            s=str(int(round(self.data.count_obs_missing_temperature))),
            fontsize=8,
            horizontalalignment="right",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-0.8,
            s="had missing ACVPU",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-1.05,
            s="had missing Heart Rate",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-1.3,
            s="had missing O2 Sats",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-1.55,
            s="had missing O2 Therapy",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-1.8,
            s="had missing Resp. Rate",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-2.05,
            s="had missing Systolic BP",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )
        plot.text(
            x=0.32,
            y=-2.3,
            s="had missing Temp.",
            fontsize=8,
            horizontalalignment="left",
            verticalalignment="bottom",
        )

        CellStyles.hide_all(plot.gca())

    def write(self) -> None:
        """
        >>> message_content = ...  # from RabbitMQ message body

        >>> SendWardReportWriter(
        ...    pdf_data=message_content,
        ...    hospital_name="Some Hospital",
        ...    ward_name="Some Ward",
        ...    location_uuid="some location",
        ...    report_month="March",
        ...    report_year="2019",
        ...).write
        """
        with self as drawer:
            # pie chart stuff
            drawer.draw_pie_chart_text()
            drawer.draw_pie_chart()
            drawer.draw_pie_chart_legend()
            drawer.draw_pie_chart_summary()
            # time series stuff
            drawer.draw_time_series_text()
            drawer.draw_time_series_percentages()
            drawer.draw_time_series_legend()
            # bar chart stuff
            drawer.draw_bar_chart_header()
            drawer.draw_bar_chart()
            drawer.draw_bar_chart_text()
            # vital signs stuff
            drawer.draw_vital_signs_recording()


class SendWardReportReader(SendWardReportIO):
    def read(self) -> bytes:
        pdf_path: Path = Path(self.file_path)
        if not pdf_path.exists():
            raise EntityNotFoundException("No ward report for location")
        return pdf_path.read_bytes()
