import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import pdfplumber  # For PDF text extraction
import tempfile
from sentence_transformers import SentenceTransformer, util
import torch


load_dotenv()

def extract_text_from_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    text = ""
    try:
        with pdfplumber.open(tmp_file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    finally:
        os.unlink(tmp_file_path)
    
    return text

model = SentenceTransformer('all-mpnet-base-v2')

def calculate_ats_score(resume_text, job_description):
    if not job_description.strip():
        return 0, []
    
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(job_description, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()
    ats_score = int(similarity * 100)

    # Keyword comparison for feedback
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', job_description.lower()))
    missing_keywords = list(jd_words - resume_words)

    return ats_score, missing_keywords[:10]
    
    
def generate_ats_feedback(ats_score, missing_keywords, job_description):
    llm = ChatGroq(temperature=0.2, model_name="meta-llama/llama-4-scout-17b-16e-instruct")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
     "You are an expert in Applicant Tracking Systems (ATS) and resume optimization. "
     "Your job is to give precise and practical advice to improve a resume’s compatibility with ATS software. "
     "You are provided with the resume's ATS score, missing keywords, and the job description. "
     "Use these inputs to suggest improvements in a crisp, professional tone. "
     "Do not ask any follow-up questions or request the resume — just give the feedback and stop."),

    ("human", 
     "ATS Score: {ats_score}\n\n"
     "Missing Keywords: {missing_keywords}\n\n"
     "Job Description:\n{job_description}\n\n"
     "Give feedback that improves the resume's ATS score by suggesting what sections to revise, which keywords to include, "
     "and what phrasing or achievements might help it better match the job description.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "ats_score": ats_score,
        "missing_keywords": missing_keywords,
        "job_description": job_description
    })
    
    return response.content

def ats_scanner():
    st.title("📝 ATS Resume Scanner")
    st.subheader("Upload your resume and job description to check ATS compatibility")
    
    with st.form("ats_scan_form"):
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
        job_description = st.text_area("Paste Job Description", height=200)
        submitted = st.form_submit_button("🔍 Scan Resume")
    
    if submitted:
        if not uploaded_file:
            st.error("Please upload your resume")
        elif not job_description.strip():
            st.error("Please paste the job description")
        else:
            with st.spinner("Analyzing resume..."):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    ats_score, missing_keywords = calculate_ats_score(resume_text, job_description)
                    
                    # Display results
                    st.metric("ATS Compatibility Score", f"{ats_score}/100")
                    st.progress(ats_score/100)
                    
                    # Show missing keywords
                    st.markdown("**Missing Keywords**")
                    for keyword in missing_keywords:
                        st.markdown(f"- `{keyword}`")
                    
                    # Generate AI feedback
                    feedback = generate_ats_feedback(ats_score, missing_keywords, job_description)
                    st.markdown(feedback)
                
                except Exception as e:
                    st.error(f"Error analyzing resume: {str(e)}")
