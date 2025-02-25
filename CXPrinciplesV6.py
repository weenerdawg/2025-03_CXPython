import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import base64

def load_checklist():
    """Loads primary and secondary CX checklist items."""
    primary = pd.read_csv('/mount/src/2025-03_cxpython/CX_Principles_Data_Cleaned.csv', delimiter=';')
    secondary = pd.read_csv('/mount/src/2025-03_cxpython/CX_Principles_Data_Cleaned.csv', delimiter=';')
    return primary, secondary

def log_assessment(name, email, project, responses, score):
    """Logs assessment responses to a CSV file without overwriting existing data."""
    log_file = "assessment_log.csv"
    log_header = ["Timestamp", "Name", "Email", "Project"] + list(responses.keys()) + ["Score"]
    log_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email, project] + list(responses.values()) + [score]
    
    try:
        with open(log_file, mode='x', newline='') as file:  # Create file if it doesn't exist
            writer = csv.writer(file)
            writer.writerow(log_header)
    except FileExistsError:
        pass
    
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(log_data)

def ask_primary_questions(primary):
    """Guides the user through the 8 primary CX questions and collects responses."""
    responses = {}
    st.header("CX Self-Assessment")
    
    options = {"No (A)": 1, "Partially (B)": 2, "Yes (C)": 3}
    
    for index, row in primary.iterrows():
        if pd.isna(row['Checklist Question']) or str(row['Checklist Question']).strip() == "":
            continue
        
        score = st.radio(f"{row['Checklist Question']}", list(options.keys()), key=f"q_{index}")
        responses[row['ID']] = options[score]
    
    return responses

def suggest_secondary_checks(primary, secondary, responses):
    """Suggests secondary checklist items based on weak areas."""
    st.header("Suggested Additional Checks")
    for primary_id, score in responses.items():
        if score < 3:
            related_checks = secondary[secondary['Primary Link'] == primary_id]
            st.subheader(f"For '{primary[primary['ID'] == primary_id]['Checklist Question'].values[0]}'")
            for _, row in related_checks.iterrows():
                st.write(f"- {row['Secondary Checklist Question']}")

def provide_feedback(name, email, project, primary, responses):
    """Provides structured feedback based on weighted scores."""
    st.header("CX Assessment Summary")
    total_score = 0
    max_score = 0
    
    for primary_id, score in responses.items():
        weight = primary[primary['ID'] == primary_id]['Weighting Score'].values[0]
        total_score += score * weight
        max_score += 3 * weight
        
        if score == 1:
            advice = primary[primary['ID'] == primary_id]['Follow-up Advice'].values[0]
            st.warning(f"❗ {primary[primary['ID'] == primary_id]['Category'].values[0]} needs improvement: {advice}")
    
    overall_percentage = (total_score / max_score) * 100
    st.subheader(f"Your overall CX Readiness Score: {overall_percentage:.2f}%")
    
    if overall_percentage > 80:
        st.success("✅ Your CX strategy is well-developed! Minor refinements needed.")
    elif overall_percentage > 50:
        st.warning("⚠️ Some key areas need improvement.")
    else:
        st.error("🚨 Significant CX gaps exist. Address high-priority items first.")
    
    log_assessment(name, email, project, responses, overall_percentage)

def get_download_link(df):
    """Generates a download link for the assessment log CSV file."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Convert to base64
    return f'<a href="data:file/csv;base64,{b64}" download="assessment_log.csv">Download Log File</a>'

def main():
    st.title("CX Checklist Self-Assessment")
    primary, secondary = load_checklist()
    
    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    project = st.text_input("Project Name")
    
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    responses = ask_primary_questions(primary)
    
    if st.button("Submit Assessment"):
        if not name or not email or not project:
            st.warning("Please fill in all the required fields before submitting.")
        else:
            st.session_state.responses = responses
            suggest_secondary_checks(primary, secondary, st.session_state.responses)
            provide_feedback(name, email, project, primary, st.session_state.responses)
    
    ##st.markdown("---")
    ##try:
    ##    log_df = pd.read_csv("assessment_log.csv")
    ##    st.markdown("### Assessment Log")
    ##    st.dataframe(log_df)
    ##    st.markdown(get_download_link(log_df), unsafe_allow_html=True)
    ##except FileNotFoundError:
    ##    st.warning("No assessment log found yet.")

if __name__ == "__main__":
    main()
