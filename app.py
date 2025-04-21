from shiny import App, render, ui
import pandas as pd
import numpy as np
import plotly.express as px

DATA_PATH = "dummy_data.csv"

CODE_TO_PROGRAM = {
    "1": "Law Librarianship",
    "2": "Law Librarianship",
    "3": "MLIS",
    "4": "MLIS",
    "5": "MSIM Online",
    "6": "MSIM",
    "7": "Museology",
    "8": "PhD"
}

LABEL_RENAMES = {
    "WEB_04": "Information<br>Usefulness",
    "WEB_06": "Information<br>Helpfulness",
    "WEB_07": "Information<br>Completeness",
    "WEB_08": "Information<br>Comprehensiveness",
    "WEB_10": "Excitement",
    "WEB_11": "Decision-<br>Making"
}


def get_filtered_data(input, df):

    selected = input.selected_participant()

    working_df = df.iloc[2:].copy()

    if "GEN_01" not in working_df.columns:
        return working_df

    working_df["ProgramLabel"] = working_df["GEN_01"].astype(str).\
        map(CODE_TO_PROGRAM)

    if selected == "All Participants":
        return working_df
    else:
        return working_df[working_df["ProgramLabel"] == selected]


def categorize_responses(col):
    conditions = [
        (col >= -2) & (col < -0.5),  # Not Helpful
        (col >= -0.5) & (col <= 0.5),  # Neutral
        (col > 0.5) & (col <= 2)  # Helpful
    ]
    labels = ["Not Helpful", "Neutral", "Helpful"]
    return pd.Series(np.select(conditions, labels, default="Missing Response"),
                     dtype="object")


def load_data():
    if DATA_PATH.endswith(".csv"):
        return pd.read_csv(DATA_PATH)
    else:
        return None


def generate_heatmap(df):
    if df is None:
        return None

    columns = ["WEB_06", "WEB_07", "WEB_08", "WEB_10", "WEB_11"]
    if not all(col in df.columns for col in columns):
        return None

    survey_corr = df[columns].dropna()
    survey_corr_numeric = survey_corr.apply(pd.to_numeric, errors="coerce")
    correlation_matrix = survey_corr_numeric.corr()
    correlation_matrix.rename(index=LABEL_RENAMES, columns=LABEL_RENAMES,
                              inplace=True)

    fig = px.imshow(correlation_matrix, text_auto=".2f",
                    color_continuous_scale=px.colors.sequential.Plasma_r,
                    title="Correlation Matrix Heatmap",
                    aspect="auto")
    fig.update_layout(
        width=800,
        height=600,
        coloraxis_colorbar=dict(thickness=30, len=1))

    return fig


def generate_trend_bar_chart(df):
    if df is None:
        return None

    survey_processed = df[["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10",
                           "WEB_11"]].apply(pd.to_numeric,
                                            errors="coerce").dropna()

    for col in ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3
        survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3

    categorized_responses = survey_processed.apply(categorize_responses)
    response_counts = categorized_responses.apply(pd.Series.value_counts)
    response_counts = response_counts.T.rename(index=LABEL_RENAMES)

    fig = px.bar(response_counts, barmode="group",
                 title="Trend of Each Question Being Helpful/Unhelpful")
    fig.update_layout(
        xaxis_tickangle=0,
        xaxis_title="",
        yaxis_title="Helpfulness Score"
    )

    return fig


def generate_pie_chart(df):
    if df is None:
        return None

    survey_processed = df[["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10",
                           "WEB_11"]].apply(pd.to_numeric,
                                            errors="coerce")

    for col in ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3
        survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3

    survey_processed["Overall_Mean"] = survey_processed.mean(axis=1,
                                                             skipna=True)
    survey_processed["Overall_Category"] = categorize_responses(
        survey_processed["Overall_Mean"])
    overall_counts = survey_processed["Overall_Category"].value_counts()
    if overall_counts.empty:
        return px.pie(title="No data available for<br>\
selected participant group.")

    fig = px.pie(names=overall_counts.index, values=overall_counts.values,
                 title="Overall Perception of<br>Website Helpfulness")

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig


def generate_importance_bar_chart(df):
    gen_05_columns = [col for col in df.columns if col.startswith("GEN_05")]
    gen_05_data = df[gen_05_columns]
    gen_05_data_avg = gen_05_data.iloc[2:].apply(pd.to_numeric,
                                                 errors="coerce"
                                                 ).dropna().mean()

    column_descriptions = {
        "GEN_05_1": "Career Services",
        "GEN_05_2": "Curriculum",
        "GEN_05_3": "Faculty",
        "GEN_05_4": "Financial Aid",
        "GEN_05_5": "Housing",
        "GEN_05_6": "Industry",
        "GEN_05_7": "Location",
        "GEN_05_8": "Research",
        "GEN_05_9": "School Reputation",
        "GEN_05_10": "Tuition"
    }

    gen_05_data_avg = gen_05_data_avg.rename(index=column_descriptions)
    fig = px.bar(x=gen_05_data_avg.index, y=gen_05_data_avg.values,
                 labels={"x": "Aspects", "y": "Mean Importance"},
                 title="Importance Scores for Grad School Aspects")

    return fig


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Filters"),
        ui.input_select("selected_participant", "Select Participant:",
                        choices=[
                            "All Participants",
                            "MSIM",
                            "MSIM Online",
                            "MLIS",
                            "PhD",
                            "Museology",
                            "Law Librarianship"],
                        selected="All Participants"
                        ),
        ui.hr(),
        "Choose the program for analyzing!"
    ),
    ui.panel_title("Survey Data Analysis"),
    ui.layout_columns(
        ui.card(ui.output_ui("pie_chart")),
        ui.card(ui.output_ui("importance_bar_chart")),
        col_widths=(4, 8)
    ),
    ui.layout_columns(
        ui.card(ui.output_ui("trend_bar_chart"))
    ),
    ui.layout_columns(
        ui.card(ui.output_ui("correlation_heatmap"))
    )
)


def server(input, output, session):
    df = load_data()

    @output
    @render.ui
    def pie_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_pie_chart(filtered_df).
                       to_html(full_html=False)) if filtered_df is not None \
            else ui.p("No data available")

    @output
    @render.ui
    def correlation_heatmap():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_heatmap(filtered_df).to_html(full_html=False))\
            if filtered_df is not None else ui.p("No data available")

    @output
    @render.ui
    def importance_bar_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_importance_bar_chart(filtered_df).
                       to_html(full_html=False)) if filtered_df is not None \
            else ui.p("No data available")

    @output
    @render.ui
    def trend_bar_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_trend_bar_chart(filtered_df).
                       to_html(full_html=False)) if filtered_df is not None \
            else ui.p("No data available")


app = App(app_ui, server)
