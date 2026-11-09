import streamlit as st
from PyPDF2 import PdfReader
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="🤖"
)

st.markdown("""
<style>
.stApp {
    background-color: #F4F8FF;
}
h1, h2, h3 {
    color: #173B70;
}
.stButton button {
    background-color: #1E66D0;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Powered Resume Matcher")
st.write("Compare your resume with a job description.")

skills_list = [
    "Python", "Java", "HTML", "CSS", "SQL",
    "Machine Learning", "Data Analysis",
    "Power BI", "Excel", "Pandas",
    "NumPy", "Deep Learning", "NLP"
]

def extract_skills(text):
    found = []
    for skill in skills_list:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found


def create_pdf_report(percentage, resume_skills,
                      required_skills, matched_skills,
                      missing_skills):

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AI Resume Matching Report", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph(
        f"Resume Match Percentage: {percentage:.2f}%",
        styles["Heading2"]
    ))

    sections = [
        ("Resume Skills", resume_skills),
        ("Required Skills", required_skills),
        ("Matched Skills", matched_skills),
        ("Missing Skills", missing_skills)
    ]

    for heading, skills in sections:
        content.append(Spacer(1, 15))
        content.append(Paragraph(heading, styles["Heading2"]))

        if skills:
            for skill in skills:
                content.append(Paragraph(
                    escape(skill), styles["Normal"]
                ))
        else:
            content.append(Paragraph("None", styles["Normal"]))

    pdf.build(content)
    buffer.seek(0)
    return buffer.getvalue()


st.header("1. Upload Your Resume")

resume = st.file_uploader(
    "Choose your Resume (PDF)",
    type=["pdf"]
)

st.header("2. Job Description")

job_description = st.text_area(
    "Paste the job description here"
)

if resume is not None and job_description.strip():

    pdf_reader = PdfReader(resume)
    resume_text = ""

    for page in pdf_reader.pages:
        resume_text += page.extract_text() or ""

    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    st.success("Resume uploaded successfully!")

    st.header("3. Resume Skills")
    st.write(resume_skills)

    st.header("4. Job Required Skills")
    st.write(required_skills)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    if required_skills:

        percentage = (
            len(matched_skills) / len(required_skills)
        ) * 100

        st.header("5. Resume Matching Result")

        st.metric(
            "Resume Match Percentage",
            f"{percentage:.2f}%"
        )

        st.progress(int(percentage))

        st.subheader("✅ Matched Skills")

        if matched_skills:
            for skill in matched_skills:
                st.success("✓ " + skill)
        else:
            st.warning("No skills matched.")

        st.subheader("6. Skill Improvement Suggestions")

        suggestions = {
            "Python": "Practice Python basics and projects.",
            "Java": "Learn Java OOP concepts and coding.",
            "SQL": "Practice SQL queries and database concepts.",
            "HTML": "Learn HTML forms and web page structure.",
            "CSS": "Practice CSS layouts and styling.",
            "Machine Learning": "Learn regression and classification algorithms.",
            "Data Analysis": "Practice data cleaning and data visualization.",
            "Power BI": "Learn dashboards and data visualization.",
            "Excel": "Practice formulas, pivot tables and charts.",
            "Pandas": "Practice data manipulation using Pandas.",
            "NumPy": "Learn arrays and numerical operations.",
            "Deep Learning": "Learn neural networks and deep learning basics.",
            "NLP": "Learn text processing and natural language processing."
        }

        if missing_skills:
            for skill in missing_skills:
                st.warning("⚠️ " + skill)
                st.info(suggestions.get(skill, "Practice this skill."))
        else:
            st.success("Great! No missing skills found.")

        st.header("7. Download Report")

        report = create_pdf_report(
            percentage,
            resume_skills,
            required_skills,
            matched_skills,
            missing_skills
        )

        st.download_button(
            label="📄 Download Matching Report (PDF)",
            data=report,
            file_name="Resume_Matching_Report.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("No supported skills found in job description.")

elif resume is None:
    st.info("Please upload your resume.")

else:
    st.info("Please enter a job description.")