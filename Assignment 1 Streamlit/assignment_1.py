import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
from fpdf import FPDF
import textwrap
from datetime import datetime
import os

FILE = r"IMB 529 Mission Hospital.xlsx"
model = joblib.load("hospital_cost_model.pkl")

df = pd.read_excel(FILE, sheet_name="MH-Raw Data")

# Header with logos
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image("hospital_logo.jpg", width=100)
with col2:
    st.title("Mission Hospital")
with col3:
    st.image("esade_logo.jpg", width=100)

st.header("Raw data")
st.write("Streamlit app to display information about total costs for the Hospital and predicting cost for new patients")

# Create tabs with content inside each tab
prediction_tab, dashboard_tab, table_tab = st.tabs(["Prediction", "Dashboard", "Table"])

# Store predictions in session state
if "dataframe_predictions" not in st.session_state:
    st.session_state.dataframe_predictions = pd.DataFrame(columns=[
        "PATIENT ID", "TIMESTAMP", "LENGTH OF STAY - ICU", "COST OF IMPLANT", "TOTAL LENGTH OF STAY", "UREA", "BMI", "COST - PREDICTED"
    ])

with prediction_tab:
    st.header("Prediction")
    st.write("Please enter the following information to make a prediction:")

    patient_id = st.text_input("Patient ID")
    length_of_stay_icu = st.number_input("Length of Stay - ICU", min_value=0, max_value=100, value=5)
    cost_of_implant = st.number_input("Cost of Implant", min_value=0.0, max_value=500000.0, value=10000.0)
    total_length_of_stay = st.number_input("Total Length of Stay", min_value=0, max_value=365, value=10)
    urea = st.number_input("Urea Level", min_value=0.0, max_value=300.0, value=50.0)
    bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=25.0)

    input_data = pd.DataFrame([[patient_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 length_of_stay_icu, cost_of_implant, total_length_of_stay, urea, bmi]],
                              columns=["PATIENT ID", "TIMESTAMP", "LENGTH OF STAY - ICU", "COST OF IMPLANT",
                                       "TOTAL LENGTH OF STAY", "UREA", "BMI"])

    if st.button("Predict Cost"):
        prediction = model.predict(input_data.iloc[:, 2:])[0]
        input_data["COST - PREDICTED"] = prediction

        st.session_state.dataframe_predictions = pd.concat(
            [st.session_state.dataframe_predictions, input_data.copy()], ignore_index=True
        )
        st.success(f"Estimated Cost: ${prediction:,.2f}")

    st.dataframe(st.session_state.dataframe_predictions)

    if not st.session_state.dataframe_predictions.empty:
        class PDFReport(FPDF):
            def __init__(self):
                super().__init__(orientation='L')

            def header(self):
                if os.path.exists("hospital_logo.jpg"):
                    self.image("hospital_logo.jpg", 10, 8, 25)
                if os.path.exists("esade_logo.jpg"):
                    self.image("esade_logo.jpg", 265, 8, 25)
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Mission Hospital - Prediction Report", ln=True, align="C")
                self.set_font("Arial", size=10)
                self.cell(0, 10, f"Downloaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
                self.ln(5)

            def prediction_table(self, df):
                self.set_font("Arial", size=8)
                line_height = self.font_size * 2
                effective_page_width = self.w - 2 * self.l_margin
                col_width = effective_page_width / len(df.columns)
                self.set_fill_color(220, 220, 220)
                for col in df.columns:
                    self.cell(col_width, line_height, col, border=1, align="C", fill=True)
                self.ln(line_height)
                for _, row in df.iterrows():
                    for col, val in zip(df.columns, row):
                        if isinstance(val, float) and col.startswith("COST"):
                            self.cell(col_width, line_height, f"${round(val, 2):,.2f}", border=1, align="C")
                        else:
                            self.cell(col_width, line_height, str(val), border=1, align="C")
                    self.ln(line_height)

        pdf = PDFReport()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.prediction_table(st.session_state.dataframe_predictions)
        pdf_path = "prediction_report.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF Report", f, file_name="prediction_report.pdf")

with dashboard_tab:
    st.header("Dashboard")
    if not df.empty:
        gender_selection = st.radio("Show information of", ["All", "Male", "Female"], key="gender_dashboard")

        if gender_selection == "Male":
            df_filtered = df[df["GENDER"] == "M"]
        elif gender_selection == "Female":
            df_filtered = df[df["GENDER"] == "F"]
        else:
            df_filtered = df

        complaint_counts = df_filtered.groupby(["KEY COMPLAINTS -CODE", "GENDER"]).size().reset_index(name="Count")
        fig_bar = px.bar(complaint_counts, x="KEY COMPLAINTS -CODE", y="Count", color="GENDER",
                         barmode="group", title="Distribution of Complaints by Gender",
                         color_discrete_map={"M": "blue", "F": "pink"})
        st.plotly_chart(fig_bar, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig_box = px.box(df_filtered, x="GENDER", y="AGE", color="GENDER", title="Age Distribution by Gender",
                         color_discrete_map={"M": "blue", "F": "pink"})
            st.plotly_chart(fig_box, use_container_width=True)
        with col2:
            implant_counts = df_filtered.groupby(["IMPLANT USED (Y/N)", "GENDER"]).size().reset_index(name="Count")
            fig_implant = px.bar(implant_counts, x="IMPLANT USED (Y/N)", y="Count", color="GENDER",
                                 barmode="group", title="Need of Implant by Gender",
                                 color_discrete_map={"M": "blue", "F": "pink"})
            st.plotly_chart(fig_implant, use_container_width=True)

with table_tab:
    st.header("Raw Hospital Data")
    st.dataframe(df)
    st.write(f"Number of rows: {df.shape[0]}")
