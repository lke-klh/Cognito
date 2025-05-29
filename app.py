from shiny import App, render, ui
import pandas as pd
import numpy as np
import plotly.express as px

DATA_PATH = "final_data.csv"

CODE_TO_PROGRAM = {
    "1": "Law Librarianship Online",
    "2": "Law Librarianship Residential",
    "3": "MLIS Online",
    "4": "MLIS Residential",
    "5": "MSIM Online",
    "6": "MSIM Residential",
    "7": "Museology",
    "8": "PhD"
}

WEB_01_LABELS = {
    "1": "Yes",
    "2": "No"
}

WEB_02_LABELS = {
    "1": "Orientation events",
    "3": "UW campus tours",
    "4": "Advising and support resources",
    "5": "Other",
    "7": "Class scheduling suggestions",
    "9": "Course descriptions"
}

color_map = {
        "Agree": "#636EFA",
        "Disagree": "#EF553B",
        "Neutral": "#00CC96"
}


def get_filtered_data(input, df):

    selected_program = input.selected_participant()
    selected_international = input.international_status()
    selected_relocation = input.relocation_status()

    working_df = df.copy()

    if "GEN_01" not in working_df.columns:
        return working_df

    working_df["GEN_01_List"] = working_df["GEN_01"].astype(str).str.split(",")
    working_df = working_df.explode("GEN_01_List")
    working_df["ProgramLabel"] = working_df["GEN_01_List"].\
        str.strip().map(CODE_TO_PROGRAM)

    if selected_program != "All Participants":
        working_df = working_df[working_df["ProgramLabel"] == selected_program]

    if "DEMO_01" in working_df.columns:
        if selected_international == "International":
            working_df = working_df[working_df["DEMO_01"].astype(str) == "1"]
        elif selected_international == "Domestic":
            working_df = working_df[working_df["DEMO_01"].astype(str) == "2"]

    if "GEN_03" in working_df.columns:
        if selected_relocation == "Yes":
            working_df = working_df[working_df["GEN_03"].astype(str) == "1"]
        elif selected_relocation == "No":
            working_df = working_df[working_df["GEN_03"].astype(str) == "2"]

    return working_df


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
        df = pd.read_csv(DATA_PATH)
        return df.iloc[2:].copy()
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
                 title="How do you feel about the website?",
                 color_discrete_map=color_map)
    fig.update_layout(
        legend_title_text=None,
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
    if df is None or df.empty:
        return None

    survey_processed = df[["WEB_04", "WEB_06", "WEB_07", "WEB_08", "WEB_10",
                           "WEB_11"]].apply(pd.to_numeric,
                                            errors="coerce").dropna()

    survey_cols = ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]
    for col in survey_cols:
        survey_processed[col] = survey_processed[col] - 3
    survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3

    overall_scores = survey_processed.mean(axis=1)
    categories = categorize_responses(overall_scores)
    counts = categories.value_counts()

    if counts.empty:
        return px.pie(title="No data available for selected group.")

    fig = px.pie(names=counts.index,
                 values=counts.values,
                 title="Is this website helpful in general?",
                 color=counts.index,
                 color_discrete_map=color_map)

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

    gen_05_data_avg = gen_05_data_avg.rename(index=column_descriptions).\
        sort_values(ascending=True)

    fig = px.bar(x=gen_05_data_avg.values, y=gen_05_data_avg.index,
                 text=gen_05_data_avg.round(2).values,
                 labels={"x": "Mean Importance Score", "y": ""},
                 title="Average Importance Scores for Grad School Information")

    return fig


def generate_web02_bar_chart(df):
    if df is None or df.empty:
        return px.bar(title="No data available for this visualization.")

    web02_split = df["WEB_02"].dropna().astype(str).str.split(",")
    web02_exploded = web02_split.explode().str.strip()

    web02_labeled = web02_exploded.map(WEB_02_LABELS)

    web02_counts = web02_labeled.value_counts().sort_values(ascending=True)

    if web02_counts.empty:
        return px.bar(title="No data available for this visualization.")

    fig = px.bar(
        x=web02_counts.values,
        y=web02_counts.index,
        text=web02_counts.values,
        labels={"x": "Number of Responses", "y": "Information Category"},
        title="What Information Do Students Seek for Their First Term?"
    )

    fig.update_layout(
        yaxis_title="",
        xaxis_title="Number of Responses"
    )

    return fig


def generate_web01_pie_chart(df):
    if df is None or df.empty:
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
        ui.input_select("selected_participant", "Select Program:",
                        choices=[
                            "All Participants",
                            "MSIM Residential",
                            "MSIM Online",
                            "MLIS Residential",
                            "MLIS Online",
                            "PhD",
                            "Museology",
                            "Law Librarianship Residential",
                            "Law Librarianship Online"],
                        selected="All Participants"
                        ),
        ui.input_select("international_status", "International vs. Domestic",
                        choices=["All", "International", "Domestic"],
                        selected="All"),
        ui.input_select("relocation_status", "Need to Relocate:",
                        choices=["All", "Yes", "No"],
                        selected="All"),
        ui.hr(),
        ui.p("Choose what to analyze!"),
        ui.p("The first filter is used for each single program. For example, "
             "if it mentions `MSIM online`, it will not contain information "
             "about the MSIM residential."),
        ui.p("The second filter is for filtering international students and "
             "domestic students."),
        ui.p("The third filter helps in seeing the different responses between"
             " students who need to relocate and those who do not.")

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
    participants assigned to various aspects of grad school. As the score \
    increases from 1-5, the importance is increased.")),
            ui.card(
                ui.output_ui("web02_bar_chart"),
                ui.p("This pie chart demonstrates what students seek for their\
     first term when looking at the website.")),
            col_widths=(6, 6)
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
    def web02_bar_chart():
        filtered_df = get_filtered_data(input, df)
        return ui.HTML(generate_web02_bar_chart(filtered_df).
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
