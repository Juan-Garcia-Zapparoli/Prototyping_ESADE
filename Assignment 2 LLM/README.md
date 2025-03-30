# 🎓 Master Finder App – Assignment 2 (LLM)

This project is part of **Assignment 2** for the course **Prototyping with LLMs** at ESADE (Second Term, MIBA).  
The goal is to build a functional prototype that uses a **Large Language Model** to assist users in exploring and comparing master's programs across different universities.

---

## 🧩 What is the utility of the prototype?

The prototype helps prospective students easily search and compare master's programs by centralizing information such as tuition fees, scholarships, duration, and location.  
It simplifies the research process and uses natural language queries to make the experience intuitive and efficient—especially useful for international students exploring global options.

---

## 🛠️ Technologies Used

| Tool/Library   | Purpose                         |
|----------------|---------------------------------|
| Streamlit      | Web app UI                      |
| Cohere         | LLM for natural language input  |
| Pandas         | Data manipulation               |
| Requests       | API interactions                |
| PyDeck         | Map visualizations              |
| FPDF           | PDF export                      |
| Pillow (PIL)   | Image handling                  |
| Dotenv         | Load environment variables      |

---

## 🚀 How to Run the App

1. Clone the repo:
   ```bash
   git clone https://github.com/Juan-Garcia-Zapparoli/Prototyping_ESADE.git
   cd Prototyping_ESADE/Assignment_2_LLM


2. Install dependencies:
    pip install -r requirements.txt

3. Create a .env file in this folder:

    COHERE_API_KEY=your_key_here
4. Run the app:
    streamlit run app.py
