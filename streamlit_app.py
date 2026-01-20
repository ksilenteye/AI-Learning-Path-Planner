import streamlit as st
import json

# Import your existing backend modules
from Input_module_LLM import generate_mcq_questions, evaluate_mcq_answers, adjust_level   # MCQ system
from LLM import generate_learning_path   # Learning path generator
# Img is optional
# from Img import generate_roadmap_image


# =====================================================
# FUNCTION — Create Formal Text Report (Not JSON)
# =====================================================
def generate_text_report(data, user_name, known_skill, verified_level):
    report = f"""
📘 **Personalized Learning Path Report**

👤 **User:** {user_name}
💡 **Skill Assessed:** {known_skill}
🎯 **Verified Skill Level:** {verified_level}

---

## 🧩 **Required Skills**
"""
    for skill in data.get("required_skills", []):
        report += f"- {skill}\n"

    report += "\n## ❗ **Missing Skills**\n"
    for skill in data.get("missing_skills", []):
        report += f"- {skill}\n"

    report += "\n---\n## 📊 **Skill Gap Analysis**\n"
    for skill, meta in data.get("skill_gap_map", {}).items():
        report += f"""
### **{skill}**
- **Why needed:** {meta.get("why_needed", "")}
- **Current Level Guess:** {meta.get("current_level_guess", "")}
- **Priority:** {meta.get("priority", "")}
"""

    report += "\n---\n## 🗓 **Weekly Learning Plan**\n"
    for idx, week in enumerate(data.get("weekly_learning_plan", []), start=1):
        report += f"""
### Week {idx} — {week.get("day", '')}
- **Topic:** {week.get("topic", '')}
- **Resource:** {week.get("resource", '')}
- **Duration:** {week.get("duration", '')}
"""

    return report


# =====================================================
# STREAMLIT UI
# =====================================================

st.set_page_config(page_title="AI Learning Path Generator", layout="wide")

st.title("🎓 AI Intelligent Learning Path Generator")
st.subheader("MCQ Verification → Skill Level → Formal Learning Path Report")


# -----------------------------------------------------
# STEP 1 — USER DETAILS
# -----------------------------------------------------
st.header("Step 1 — Enter Your Profile")

name = st.text_input("Your Name")
known_skill = st.text_input("Known Skill (e.g., Python, ML, SQL)")

skill_level = st.selectbox(
    "Your Self-Rated Level",
    ["Beginner", "Intermediate", "Advanced"]
)

skills_to_learn = st.text_input("Skills you want to learn (comma separated)")
career_goals = st.text_input("Career Goals (comma separated)")

learning_speed = st.selectbox("Learning Speed", ["slow", "medium", "fast"])
preferred_format = st.selectbox("Preferred Format", ["video", "text", "project-based"])

generate_mcqs_btn = st.button("Generate MCQs")


# -----------------------------------------------------
# STEP 2 — DISPLAY MCQs
# -----------------------------------------------------
if generate_mcqs_btn:
    if not known_skill.strip():
        st.error("Please enter a known skill before generating MCQs.")
    else:
        mcqs = generate_mcq_questions(known_skill, skill_level)
        st.session_state["mcqs"] = mcqs
        st.success("MCQs generated!")

if "mcqs" in st.session_state:
    st.header("Step 2 — Answer the MCQs")

    mcqs = st.session_state["mcqs"]
    user_answers = []

    for idx, q in enumerate(mcqs):
        # Remove the correct answer from display
        display_q = q.split("Correct Answer:")[0].strip()

        st.write(f"### Question {idx+1}")
        st.write(display_q.replace("\n", "  \n"))

        ans = st.radio(
            f"Your answer for Q{idx+1}",
            ["A", "B", "C", "D"],
            key=f"ans_{idx}"
        )
        user_answers.append(ans)

    verify_btn = st.button("Verify Level")

    if verify_btn:
        correct = evaluate_mcq_answers(mcqs, user_answers)
        verified_level = adjust_level(skill_level, correct)

        st.session_state["verified_level"] = verified_level
        st.session_state["correct_answers"] = correct

        st.success(f"Correct Answers: {correct}/5")
        st.info(f"Your Verified Level: **{verified_level}**")


# -----------------------------------------------------
# STEP 3 — GENERATE LEARNING PATH
# -----------------------------------------------------
if "verified_level" in st.session_state:
    st.header("Step 3 — Generate Your Personalized Learning Path")

    if st.button("Generate My Learning Path"):
        profile = {
            "name": name,
            "known_skills": [known_skill],
            "known_skills_with_levels": f"{known_skill} ({st.session_state['verified_level']})",
            "skills_to_learn": [s.strip() for s in skills_to_learn.split(",") if s.strip()],
            "career_goals": [c.strip() for c in career_goals.split(",") if c.strip()],
            "learning_speed": learning_speed,
            "preferred_format": preferred_format
        }

        result = generate_learning_path(profile)
        st.session_state["roadmap"] = result
        st.success("Learning Path Generated!")

        # -----------------------------------------------------
        # STEP 4 — SHOW TEXT REPORT
        # -----------------------------------------------------
        st.header("📘 Your Personalized Learning Path Report")

        report_text = generate_text_report(
            result,
            name,
            known_skill,
            st.session_state["verified_level"]
        )

        st.markdown(report_text)

        # Download button
        st.download_button(
            "Download Report (TEXT)",
            report_text,
            "learning_path_report.txt"
        )
