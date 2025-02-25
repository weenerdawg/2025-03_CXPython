import streamlit as st
import pandas as pd

def load_checklist():
    """Loads primary and secondary CX checklist items."""
    primary = pd.read_csv('/mount/src/2025-03_cxpython/CX_Principles_Data_Cleaned.csv', delimiter=';')
    secondary = pd.read_csv('/mount/src/2025-03_cxpython/CX_Principles_Data_Cleaned.csv', delimiter=';')
    return primary, secondary

def ask_primary_questions(primary):
    """Guides the user through the 8 primary CX questions and collects responses."""
    responses = {}
    st.header("CX Self-Assessment")
    
    for index, row in primary.iterrows():
        if pd.isna(row['Checklist Question']) or str(row['Checklist Question']).strip() == "":
            continue
        
        score = st.radio(f"{row['Checklist Question']} (1-3):", [1, 2, 3], key=f"q_{index}")
        responses[row['ID']] = score
    
    return responses

def suggest_secondary_checks(primary, secondary, responses):
    """Suggests secondary checklist items based on weak areas."""
    st.header("Suggested Additional Checks")
    for primary_id, score in responses.items():
        if score < 2:
            related_checks = secondary[secondary['Primary Link'] == primary_id]
            st.subheader(f"For '{primary[primary['ID'] == primary_id]['Checklist Question'].values[0]}'")
            for _, row in related_checks.iterrows():
                st.write(f"- {row['Secondary Checklist Question']}")

def provide_feedback(primary, responses):
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

def main():
    st.title("CX Checklist Self-Assessment")
    primary, secondary = load_checklist()
    
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    responses = ask_primary_questions(primary)
    
    if st.button("Submit Assessment"):
        st.session_state.responses = responses
        suggest_secondary_checks(primary, secondary, st.session_state.responses)
        provide_feedback(primary, st.session_state.responses)

if __name__ == "__main__":
    main()
