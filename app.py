from shiny import App, render, ui
import pandas as pd
import numpy as np
import plotly.express as px

DATA_PATH = "final_data.csv"

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

DEMO_03_LABELS = {
    "1": "Professional Employment",
    "2": "Further Academic Study",
    "3": "Start Own Business",
    "4": "Not Sure",
    "5": "Other"
}

WEB_01_LABELS = {
    "1": "Yes",
    "2": "No"
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
        (col >= -2) & (col < -0.5),  # Disagree
        (col >= -0.5) & (col <= 0.5),  # Neutral
        (col > 0.5) & (col <= 2)  # Agree
    ]
    labels = ["Disagree", "Neutral", "Agree"]
    return pd.Series(np.select(conditions, labels, default="Missing Response"),
                     dtype="object")


def load_data():
    if DATA_PATH.endswith(".csv"):
        return pd.read_csv(DATA_PATH)
    else:
        return None


def generate_bar_chart(df):
    if df is None:
        return None

    survey_processed = df[["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10",
                           "WEB_11"]].apply(pd.to_numeric,
                                            errors="coerce").dropna()

    for col in ["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3

    survey_processed = survey_processed.rename(columns={
        "WEB_04": "The website is easy to navigate ",
        "WEB_06": "The information is helpful ",
        "WEB_07": "The website is missing information ",
        "WEB_08": "The information is comprehensive ",
        "WEB_10": "It makes me feel excited about the program ",
        "WEB_11": "It helps me decide to commit to UW "
    })

    categorized_responses = survey_processed.apply(categorize_responses)
    response_counts = categorized_responses.apply(pd.Series.value_counts).T
    response_percent = response_counts.div(response_counts.sum(axis=1),
                                           axis=0) * 100

    fig = px.bar(response_percent, orientation="h", barmode="stack",
                 labels={"value": "Percentage (%)", "index": "Metric"},
                 title="How do you feel about the website?")
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Answer's Percentage",
        xaxis=dict(
            tickmode="linear",
            tick0=0,
            dtick=20,
            range=[0, 100]
        )
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


def generate_demo03_pie_chart(df):
    if df is None:
        return px.pie(title="No data available for this visualization.")

    demo_data = df["DEMO_03"].astype(str)
    demo_data_labeled = demo_data.map(DEMO_03_LABELS).\
        fillna("Missing Response")

    demo_counts = demo_data_labeled.value_counts()

    if demo_counts.empty:
        return px.pie(title="No data available for this visualization.")

    fig = px.pie(
        names=demo_counts.index,
        values=demo_counts.values,
        title="Distribution of Primary Goal<br>after Graduation"
    )

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


def generate_web01_pie_chart(df):
    if df is None:
        return px.pie(title="No data available for this visualization.")

    demo_data = df["WEB_01"].astype(str)
    demo_data_labeled = demo_data.map(WEB_01_LABELS).\
        fillna("Missing Response")

    demo_counts = demo_data_labeled.value_counts()

    if demo_counts.empty:
        return px.pie(title="No data available for this visualization.")

    fig = px.pie(
        names=demo_counts.index,
        values=demo_counts.values,
        title="Use of Website Prior to Survey"
    )

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
    ui.div(
        ui.layout_columns(
            ui.card(
                ui.output_ui("pie_chart"),
                ui.p("This pie chart shows the overall perception of \
    the website's helpfulness based on participant responses.")),
            ui.card(
                ui.output_ui("bar_chart"),
                ui.p("This bar chart highlights how each survey question was \
    rated agree or disagree in terms of proportion.")
            ),
            col_widths=(4, 8)
        ),
        class_="mb-4"
    ),
    ui.div(
        ui.layout_columns(
            ui.card(
                ui.output_ui("importance_bar_chart"),
                ui.p("This bar chart displays the average importance ratings \
    participants assigned to various aspects of grad school.")),
            ui.card(
                ui.output_ui("demo03_pie_chart"),
                ui.p("This pie chart demonstrates the distribution of \
    students' primary goal after graduations.")),
            col_widths=(8, 4)
        ),
        class_="mb-4"
    ),
    ui.card(
        ui.output_ui("web01_pie_chart"),
        ui.p("This pie chart demonstrates the distribution of students' \
    use of website prior to the survey."))
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
    def importance_bar_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_importance_bar_chart(filtered_df).
                       to_html(full_html=False)) if filtered_df is not None \
            else ui.p("No data available")

    @output
    @render.ui
    def bar_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_bar_chart(filtered_df).
                       to_html(full_html=False)) if filtered_df is not None \
            else ui.p("No data available")

    @output
    @render.ui
    def demo03_pie_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_demo03_pie_chart(filtered_df).
                       to_html(full_html=False)) \
            if filtered_df is not None else ui.p("No data available")

    @output
    @render.ui
    def web01_pie_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_web01_pie_chart(filtered_df).
                       to_html(full_html=False)) \
            if filtered_df is not None else ui.p("No data available")


app = App(app_ui, server)
