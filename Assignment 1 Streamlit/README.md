# 🏥 Mission Hospital Cost Prediction App

This Streamlit web application allows users to:

- Predict the estimated **cost of treatment** for new patients using a machine learning model.
- Visualize hospital statistics (complaints, age, implants) by gender.
- Export predictions to a **PDF report** with logos, formatting, and timestamp.
- Display the original dataset from the hospital.

---

## 📁 Folder Structure

```
.
├── assignment_1.py               # Streamlit app source code
├── hospital_cost_model.pkl       # Trained RandomForestRegressor model
├── IMB 529 Mission Hospital.xlsx # Dataset with raw hospital data
├── hospital_logo.jpg             # Mission Hospital logo
├── esade_logo.jpg                # ESADE logo
├── prediction_report.pdf         # Auto-generated PDF report
├── requirements.txt              # Python dependencies
```

---

## 📊 App Features

### 🔮 1. Prediction Tab
- Input patient data: ICU stay, implant cost, total stay, UREA level, BMI
- Predict cost using a trained `RandomForestRegressor`
- View past predictions with timestamps
- Download all predictions in a styled PDF with logos

### 📈 2. Dashboard Tab
- Complaint distribution by gender
- Age distribution (box plot by gender)
- Implant usage by gender
- Gender filter built into the tab

### 🧾 3. Table Tab
- Displays full dataset from the Excel file (sheet: `MH-Raw Data`)
- Row count included

---

## 📦 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

### `requirements.txt` includes:
```
streamlit
pandas
plotly
joblib
fpdf
openpyxl
```

---

## 🚀 How to Run

In your terminal:

```bash
streamlit run assignment_1.py
```

Make sure all assets (logos, Excel, model) are in the same folder.

---

## 💡 Model Info

- Trained using scikit-learn’s `RandomForestRegressor`
- Trained on the top 5 most important numerical features
- Saved with `joblib` as `hospital_cost_model.pkl`

---

Created by Juan Pablo – ESADE MIBA 2024–2025 🌍