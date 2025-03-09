from shiny import App, render, ui
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile


DATA_PATH = "/Users/keki3215/Documents/capstone/dummy_data.csv"


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

    plt.figure(figsize=(5, 3))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f",
                cmap="coolwarm", center=0, linewidths=.5)
    for i in range(len(correlation_matrix.columns)):
        plt.gca().add_patch(plt.Rectangle((i, i), 1, 1,
                                          fill=True, color="grey", lw=0))
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, format="png")
    plt.close()

    return temp_file.name


def generate_trend_bar_chart(df):
    if df is None:
        return None
    survey_processed = df[["WEB_04", "WEB_06", "WEB_07",
                           "WEB_08", "WEB_10", "WEB_11"]].\
        apply(pd.to_numeric, errors="coerce")
    survey_processed = survey_processed.dropna()

    for col in ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3
        survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3
        survey_processed.sample(5)

    categorized_responses = survey_processed.apply(categorize_responses)
    response_counts = categorized_responses.apply(pd.Series.value_counts)

    response_counts.T.plot(kind="bar", color=plt.cm.Paired(np.arange(
        len(response_counts))), figsize=(6, 3), width=0.8)
    plt.xlabel("Questions")
    plt.ylabel("Number of Responses")
    plt.legend(title="Categories",
               labels=["Not Helpful", "Neutral", "Helpful"])
    plt.xticks(rotation=0)
    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, format="png")
    plt.close()

    return temp_file.name


def generate_pie_chart(df):
    if df is None:
        return None
    survey_processed = df[["WEB_04", "WEB_06", "WEB_07",
                           "WEB_08", "WEB_10", "WEB_11"]].\
        apply(pd.to_numeric, errors="coerce")
    survey_processed = survey_processed.dropna()

    for col in ["WEB_04", "WEB_06", "WEB_08", "WEB_10", "WEB_11"]:
        survey_processed[col] = survey_processed[col] - 3
        survey_processed["WEB_07"] = 6 - survey_processed["WEB_07"] - 3
        survey_processed.sample(5)

    survey_processed["Overall_Mean"] = survey_processed.mean(axis=1,
                                                             numeric_only=True)
    survey_processed["Overall_Category"] = categorize_responses(
        survey_processed["Overall_Mean"])
    overall_counts = survey_processed["Overall_Category"].value_counts()

    plt.figure(figsize=(3, 3))
    overall_counts.plot(kind="pie", autopct='%1.1f%%', startangle=90,
                        colors=plt.cm.Paired(np.arange(len(overall_counts))),
                        labels=["Not Helpful", "Neutral", "Helpful"])
    plt.ylabel("")

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, format="png")
    plt.close()

    return temp_file.name


def generate_importance_bar_chart(df):
    gen_05_columns = [col for col in df.columns if col.startswith("GEN_05")]
    gen_05_data = df[gen_05_columns]
    gen_05_data_avg = gen_05_data.iloc[2:].apply(pd.to_numeric,
                                                 errors="coerce").\
        dropna().mean()

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
    plt.figure(figsize=(6, 3))
    gen_05_data_avg.plot(kind="bar", color="skyblue")
    plt.xlabel("Aspects")
    plt.ylabel("Mean Importance")
    plt.xticks(rotation=45)
    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, format="png")
    plt.close()

    return temp_file.name


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Filters"),
        ui.input_select("selected_participant", "Select Participant:",
                        choices=["All Participants", "MSIM",
                                 "MSIM Online", "MLIS", "PhD"],
                        selected="All Participants"),
        ui.hr(),
        "Filtering runction yet to come"
    ),

    ui.panel_title("Survey Data Analysis"),

    ui.layout_columns(
        ui.card(
            # ui.h4("Overall Perception of Website Helpfulness"),
            ui.output_image("pie_chart"),
        ),
        ui.card(
            # ui.h4("Trend of Each Question Being Helpful/Unhelpful"),
            ui.output_image("trend_bar_chart"),
        ),
        col_widths=(4, 8), row_heights="300px"
    ),
    ui.layout_columns(
        ui.card(
            # ui.h4("Importance Scores for Grad School Aspects"),
            ui.output_image("importance_bar_chart"),
        ),
        ui.card(
            # ui.h4("Correlation Matrix Heatmap"),
            ui.output_image("correlation_heatmap"),
        ),
        col_widths=(8, 4), row_heights="300px"
    )
)


def server(input, output, session):
    df = load_data()

    @output
    @render.image
    def pie_chart():
        if df is None:
            return None
        pie_path = generate_pie_chart(df)
        return {"src": pie_path, "alt": "Overall Perception Pie Chart"}

    @output
    @render.image
    def correlation_heatmap():
        if df is None:
            return None
        heatmap_path = generate_heatmap(df)
        return {"src": heatmap_path, "alt": "Correlation Matrix Heatmap"}

    @output
    @render.image
    def importance_bar_chart():
        importance_path = generate_importance_bar_chart(df)
        return {"src": importance_path,
                "alt": "Average Importance Scores for Grad School Aspects"}

    @output
    @render.image
    def trend_bar_chart():
        if df is None:
            return None
        trend_path = generate_trend_bar_chart(df)
        return {"src": trend_path,
                "alt": "Trend of Each Question Being Helpful/Unhelpful"}


app = App(app_ui, server)
