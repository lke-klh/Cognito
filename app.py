from shiny import App, render, ui
import pandas as pd
import numpy as np
import plotly.express as px

DATA_PATH = "../dummy_data.csv"


def categorize_responses(col):
    conditions = [
        (col >= -2) & (col < -0.5),  # Not Helpful
        (col >= -0.5) & (col <= 0.5),  # Neutral
        (col > 0.5) & (col <= 2)  # Helpful
    ]
    labels = ["Not Helpful", "Neutral", "Helpful"]
    return pd.Series(np.select(conditions, labels, default="Unknown"),
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

    fig = px.imshow(correlation_matrix, text_auto=True,
                    color_continuous_scale=px.colors.sequential.Plasma_r,
                    title="Correlation Matrix Heatmap")
    fig.update_layout(coloraxis_colorbar=dict(thickness=15, len=0.5))

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

    fig = px.bar(response_counts.T, barmode="group",
                 labels={"x": "Aspects", "y": "Mean Importance"},
                 title="Trend of Each Question Being Helpful/Unhelpful")

    return fig


def generate_pie_chart(df):
    if df is None:
        return None

    survey_processed = df[["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10",
                           "WEB_11"]].apply(pd.to_numeric,
                                            errors="coerce").dropna()

    for col in ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3
        survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3

    survey_processed["Overall_Mean"] = survey_processed.mean(axis=1,
                                                             numeric_only=True)
    survey_processed["Overall_Category"] = categorize_responses(
        survey_processed["Overall_Mean"])
    overall_counts = survey_processed["Overall_Category"].value_counts()

    fig = px.pie(names=overall_counts.index, values=overall_counts.values,
                 title="Overall Perception of Website Helpfulness")

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
                        choices=["All Participants", "MSIM", "MSIM Online",
                                 "MLIS", "PhD"],
                        selected="All Participants"),
        ui.hr(),
        "Filtering function yet to come"
    ),
    ui.panel_title("Survey Data Analysis"),
    ui.layout_columns(
        ui.card(ui.output_ui("pie_chart")),
        ui.card(ui.output_ui("trend_bar_chart")),
        col_widths=(4, 8)
    ),
    ui.layout_columns(
        ui.card(ui.output_ui("importance_bar_chart")),
        ui.card(ui.output_ui("correlation_heatmap")),
        col_widths=(8, 4)
    )
)


def server(input, output, session):
    df = load_data()

    @output
    @render.ui
    def pie_chart():
        return ui.HTML(generate_pie_chart(df).to_html(full_html=False))\
            if df is not None else ui.p("No data available")

    @output
    @render.ui
    def correlation_heatmap():
        return ui.HTML(generate_heatmap(df).to_html(full_html=False))\
            if df is not None else ui.p("No data available")

    @output
    @render.ui
    def importance_bar_chart():
        return ui.HTML(generate_importance_bar_chart(df).
                       to_html(full_html=False)) if df is not None else ui.p(
                           "No data available")

    @output
    @render.ui
    def trend_bar_chart():
        return ui.HTML(generate_trend_bar_chart(df).
                       to_html(full_html=False)) if df is not None else ui.p(
                           "No data available")


app = App(app_ui, server)
