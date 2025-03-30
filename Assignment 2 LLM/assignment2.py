import streamlit as st
import cohere
import pandas as pd
import requests
import pydeck as pdk
from dotenv import load_dotenv
import os
from fpdf import FPDF
from datetime import datetime
from PIL import Image
import urllib.request


load_dotenv()
api_key = os.getenv("COHERE_API_KEY")

# Initialize Cohere
co = cohere.Client(api_key) 

# QS ranking sample
qs_ranking = {
    "ESADE": 151,
    "Nova Tech Business School": 500,
    "Berlin Tech University": 220,
    "Milano School of Innovation": 310
}

# Simulated data
program_data = [
    {
        "university": "ESADE",
        "programs": [
            {
                "name": "Master in Data Analytics and Artificial Intelligence",
                "description": "Develop the skills to analyze data and apply insights using Python, AI tools, and big data platforms like AWS and Spark.",
                "area": "Data",
                "cost": "35,000.00 euros",
                "location": "San Cugat del Valles, Barcelona",
                "country": "Spain",
                "scholarship": "Yes, depends",
                "modality": "In person",
                "courses": [
                    "Artificial Intelligence I", "Business in Society", "Cloud Computing",
                    "Python for Data Science", "Artificial Intelligence II",
                    "Data Analytics with R", "Thinking with Data"
                ]
            },
            {
                "name": "Master in Innovation & Entrepreneurship",
                "description": "Launch your own startup or drive innovation within a company using strategy, marketing, and creative design tools.",
                "area": "Business",
                "cost": "35,000.00 euros",
                "location": "San Cugat del Valles, Barcelona",
                "country": "Spain",
                "scholarship": "Yes, depends",
                "modality": "In person",
                "courses": [
                    "Business in Society", "Creative Thinking", "Entrepreneurship",
                    "Innovation Management", "Finance for Entrepreneurs",
                    "Marketing for Entrepreneurs"
                ]
            }
        ]
    },
    {
        "university": "Nova Tech Business School",
        "programs": [
            {
                "name": "Master in Data Intelligence and AI Strategy",
                "description": "Focus on leveraging data, AI platforms, and analytics to drive innovation and strategic decisions.",
                "area": "Data",
                "cost": "35,000.00 euros",
                "location": "Madrid",
                "country": "Spain",
                "scholarship": "Yes, depends",
                "modality": "In person",
                "courses": [
                    "Artificial Intelligence II", "Data Visualization", "Cloud Computing",
                    "Python for Data Science", "AI for Decision Making", "Big Data Infrastructure"
                ]
            },
            {
                "name": "Master in Creative Innovation & Startup Development",
                "description": "Train to design, fund, and grow new business models with a strong focus on entrepreneurial thinking and innovation ecosystems.",
                "area": "Business",
                "cost": "35,000.00 euros",
                "location": "Madrid",
                "country": "Spain",
                "scholarship": "Yes, depends",
                "modality": "In person",
                "courses": [
                    "Entrepreneurship", "Creative Thinking", "Design Thinking",
                    "Finance for Entrepreneurs", "Startup Marketing", "Innovation Management"
                ]
            }
        ]
    },
    {
        "university": "Berlin Tech University",
        "programs": [
            {
                "name": "MSc in Intelligent Systems and Data Science",
                "description": "An interdisciplinary program focused on AI systems, data engineering, and computational logic for smart environments.",
                "area": "Data",
                "cost": "Free (tuition-free)",
                "location": "Berlin",
                "country": "Germany",
                "scholarship": "Limited",
                "modality": "In person",
                "courses": [
                    "Machine Learning", "Big Data Systems", "AI & Society",
                    "Deep Learning", "Cloud Architecture", "Data Ethics"
                ]
            }
        ]
    },
    {
        "university": "Milano School of Innovation",
        "programs": [
            {
                "name": "Master in Design Thinking and Digital Strategy",
                "description": "Equips students with the mindset and skills to lead design-driven innovation in tech-oriented organizations.",
                "area": "Business",
                "cost": "19,500.00 euros",
                "location": "Milan",
                "country": "Italy",
                "scholarship": "Yes",
                "modality": "Hybrid",
                "courses": [
                    "Design Thinking", "Strategic Innovation", "UX & Digital Interfaces",
                    "Agile Management", "Startup Launch Lab", "Behavioral Economics"
                ]
            }
        ]
    }
]

# Streamlit config
st.set_page_config(page_title="Master Finder App", page_icon="🎓")
col1, col2 = st.columns([1, 5])
with col1:
    st.image("master_finder_app.png", width=100)
with col2:
    st.markdown("""
        <h1 style='margin-top: 10px;'>Master's Degree Finder</h1>
    """, unsafe_allow_html=True)

if "selected_countries" not in st.session_state:
    st.session_state.selected_countries = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Program Finder"

class PDF(FPDF):
    def header(self):
        if os.path.exists("master_finder_app.png"):
            self.image("master_finder_app.png", 10, 5, 20)
        self.set_font("Arial", "B", 10)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, "Master's Program Recommendation Report", ln=True, align="C", fill=True)
        self.ln(10)

    def program_table(self, df):
        self.set_font("Arial", size=6)
        col_width = self.w / len(df.columns) - 2
        self.ln(2)
        for col in df.columns:
            self.cell(col_width, 5, str(col).encode("latin-1", errors="replace").decode("latin-1"), border=1, align="C")
        self.ln()
        for _, row in df.iterrows():
            for val in row:
                val = str(val).encode("latin-1", errors="replace").decode("latin-1")
                self.cell(col_width, 5, val, border=1, align="C")
            self.ln()

    def country_info(self, country_infos):
        self.ln(3)
        self.set_font("Arial", "B", 8)
        self.cell(0, 6, "Country Information", ln=True)
        self.set_font("Arial", size=6)
        for country, info in country_infos.items():
            self.ln(2)
            self.cell(0, 4, f"- {country}".encode("latin-1", errors="replace").decode("latin-1"), ln=True)
            for key, val in info.items():
                line = f"   {key}: {val}"
                self.cell(0, 4, line.encode("latin-1", errors="replace").decode("latin-1"), ln=True)

def extract_keywords_prompt(user_input):
    return f"""
    From the following user profile, extract key interests, preferred study fields (e.g., Data, Business), and career motivations.
    User profile:
    {user_input}
    Return the result as a comma-separated list of keywords.
    """

def explain_matches_prompt(user_input, match_names):
    return f"""
    User background: {user_input}
    Programs matched: {match_names}
    Based on the user's interests and academic goals, explain in 2–3 sentences per program why each one would be a suitable match.
    """

def gap_analysis_prompt(user_input):
    return f"""
    User profile: {user_input}
    Based on this profile, are there any types of master's programs or study areas NOT listed above that could still be a good fit? Suggest a few ideas and why.
    """

if st.session_state.current_page == "Program Finder":
    min_rank, max_rank = st.slider("Filter by QS World Ranking (lower is better)", 1, 1000, (1, 1000))
    user_input = st.text_area("Describe your background and interests:", placeholder="e.g. I want to launch a startup")

    if user_input:
        with st.spinner("Finding matching programs..."):
            keywords_prompt = extract_keywords_prompt(user_input)
            keywords = co.chat(model="command-r-plus", message=keywords_prompt).text.strip().lower().split(",")

            matches = []
            for uni in program_data:
                for prog in uni["programs"]:
                    text = (prog["name"] + prog["description"] + " ".join(prog["courses"])).lower()
                    rank = qs_ranking.get(uni["university"], 1001)
                    if any(k.strip() in text for k in keywords) and min_rank <= rank <= max_rank:
                        prog_copy = prog.copy()
                        prog_copy["university"] = uni["university"]
                        prog_copy["qs_rank"] = rank
                        matches.append(prog_copy)

            if matches:
                df = pd.DataFrame(matches)[["university", "name", "area", "cost", "location", "modality", "scholarship", "qs_rank", "country"]]

                match_names = [f"{m['name']} at {m['university']}" for m in matches]
                explain_prompt = explain_matches_prompt(user_input, match_names)
                explanation = co.chat(model="command-r-plus", message=explain_prompt).text.strip()

                st.subheader("🔍 Suggested Programs")
                st.write(explanation)
                st.dataframe(df)

                if st.checkbox("🔧 Show additional suggestions"):
                    gap_prompt = gap_analysis_prompt(user_input)
                    gap_response = co.chat(model="command-r-plus", message=gap_prompt)
                    st.subheader("💡 Other Possible Program Ideas")
                    st.write(gap_response.text.strip())

                st.subheader("📍 Locations Map")
                map_df = df.copy()
                map_df["lat"] = map_df["location"].map({
                    "San Cugat del Valles, Barcelona": 41.4722,
                    "Madrid": 40.4168,
                    "Berlin": 52.52,
                    "Milan": 45.4642
                })
                map_df["lon"] = map_df["location"].map({
                    "San Cugat del Valles, Barcelona": 2.0812,
                    "Madrid": -3.7038,
                    "Berlin": 13.405,
                    "Milan": 9.19
                })
                map_df["tooltip"] = map_df["name"] + " - " + map_df["university"]

                st.pydeck_chart(pdk.Deck(
                    initial_view_state=pdk.ViewState(latitude=map_df["lat"].mean(), longitude=map_df["lon"].mean(), zoom=4),
                    layers=[pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_radius=40000, get_color='[200, 30, 0, 160]', pickable=True)],
                    tooltip={"text": "{tooltip}"}
                ))

                if st.button("🌐 See country details", key="country_details_btn"):
                    st.session_state.selected_countries = list(df["country"].unique())
                    st.session_state.current_page = "Country Info"
                    st.experimental_rerun()

                if st.button("🖨️ Download PDF Report"):
                    pdf = PDF(orientation="L")
                    pdf.add_page()
                    pdf.program_table(df)

                    countries = list(df["country"].unique())
                    country_infos = {}
                    for country in countries:
                        try:
                            url = f"https://restcountries.com/v3.1/name/{country.lower()}?fullText=true"
                            res = requests.get(url)
                            data = res.json()[0]
                            info = {
                                "Capital": data.get("capital", ["N/A"])[0],
                                "Population": f"{data.get('population', 0):,}",
                                "Region": data.get("region", "N/A"),
                                "Currency": list(data.get("currencies", {}).keys())[0],
                                "Languages": ", ".join(data.get("languages", {}).values())
                            }
                            country_infos[country] = info
                        except:
                            continue

                    pdf.add_page()
                    pdf.country_info(country_infos)

                    filename = f"master_finder_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf.output(filename)
                    st.success(f"PDF report saved as `{filename}`")
            else:
                st.warning("No matches found. Try adjusting your profile.")

elif st.session_state.current_page == "Country Info":
    st.title("🌍 Country Information")
    for country in st.session_state.selected_countries:
        st.markdown("---")
        st.subheader(f"🇺🇳 Info for {country}")
        try:
            url = f"https://restcountries.com/v3.1/name/{country.lower().strip()}?fullText=true"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()[0]
                st.write(f"**Capital**: {data.get('capital', ['N/A'])[0]}")
                st.write(f"**Population**: {data.get('population', 'N/A'):,}")
                st.write(f"**Region**: {data.get('region', 'N/A')}")
                currencies = list(data.get('currencies', {}).keys())
                st.write(f"**Currency**: {currencies[0] if currencies else 'N/A'}")
                languages = data.get('languages', {})
                st.write(f"**Languages**: {', '.join(languages.values()) if languages else 'N/A'}")
                st.image(data.get('flags', {}).get('png', ''), caption=f"Flag of {country}")
            else:
                st.error("Data not available.")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("⬅️ Back to program finder"):
        st.session_state.current_page = "Program Finder"
        st.experimental_rerun()
