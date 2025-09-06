import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from docx import Document
import io

# -------------------- Load Environment Variables -------------------- #
load_dotenv()  # Reads .env file

# -------------------- Helper Functions -------------------- #

def create_docx(resume_text):
    """Create a Word document from resume text."""
    doc = Document()
    for line in resume_text.split("\n"):
        doc.add_paragraph(line)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_resume_prompt():
    """Define the system + human prompt for Groq."""
    return ChatPromptTemplate.from_messages([
        ("system", """You are RESUME_BUILDER PRO, an AI assistant that creates professional resumes based on user-provided information. STRICTLY use ONLY the information provided by the user. Do not add, infer, or invent any information.

Your task:
1. Analyze the provided details.
2. Generate a well-structured, ATS-friendly resume in markdown.
3. Use first-person phrasing.
4. Follow professional formatting and include industry keywords.
5. Include a concise career summary at the end (4-5 sentences).

Resume Structure:
[Header] Name | Contact Info | Portfolio/LinkedIn
[Professional Summary] 2-3 sentences
[Work Experience] - Position @ Company (Dates) • Bullet points
[Education] Degree @ Institution (Year)
[Skills] Technical & Soft skills
[Additional Sections] Certifications | Projects | Languages"""),
        
        ("human", """Create a professional resume with these details:

Personal Information:
- Name: {name}
- Email: {email}
- Phone: {phone}
- LinkedIn/Portfolio: {portfolio}
- Target Job Title: {target_job}

Education:
{education}

Work Experience:
{experience}

Skills:
{skills}

Additional Information:
{additional_info}

Job Description/Requirements:
{job_description}

Special Instructions:
{special_instructions}""")
    ])

def generate_resume(user_inputs):
    """Generate a resume using Groq API."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Groq API key not found. Please set GROQ_API_KEY in your .env or Streamlit secrets.")

    llm = ChatGroq(
        api_key=groq_api_key,
        temperature=0.3,
        model_name="compound-beta"
    )
    prompt = create_resume_prompt()
    chain = prompt | llm
    response = chain.invoke(user_inputs)
    return response.content

# -------------------- Streamlit App -------------------- #

def main():
    st.title("📄 AI Resume Builder Pro")
    st.subheader("Create a professional resume in minutes")

    with st.expander("⚙️ Enter Your Information", expanded=True):
        with st.form("resume_form"):

            # -------------------- User Details -------------------- #
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", placeholder="John Doe")
                email = st.text_input("Email*", placeholder="john@example.com")
                phone = st.text_input("Phone*", placeholder="(123) 456-7890")
            with col2:
                portfolio = st.text_input("LinkedIn/Portfolio", placeholder="linkedin.com/in/johndoe")
                target_job = st.text_input("Target Job Title*", placeholder="Software Engineer")
            
            st.markdown("**Education**")
            education = st.text_area(
                "List your education (Degree, Institution, Year, Honors)",
                placeholder="BSc Computer Science @ XYZ University (2023)\n- GPA: 3.8\n- Relevant Coursework: Data Structures, Algorithms",
                height=100
            )
            
            st.markdown("**Work Experience**")
            experience = st.text_area(
                "List your work experience (Company, Position, Dates, Achievements)",
                placeholder="Software Developer @ ABC Corp (2021-2023)\n- Developed 3 web applications using Python and React\n- Improved system performance by 40%",
                height=150
            )
            
            st.markdown("**Skills**")
            skills = st.text_area(
                "List your skills (Separate by category if possible)",
                placeholder="Programming: Python, JavaScript, SQL\nTools: Git, Docker, AWS\nSoft Skills: Team Leadership, Problem Solving",
                height=100
            )
            
            st.markdown("**Additional Information**")
            additional_info = st.text_area(
                "Certifications, Projects, Languages, etc.",
                placeholder="Certifications: AWS Certified Developer\nProjects: Personal portfolio website\nLanguages: English (Fluent), Spanish (Intermediate)",
                height=100
            )
            
            st.markdown("**Job Description (Optional)**")
            job_description = st.text_area(
                "Paste the job description you're applying for",
                placeholder="Helps tailor your resume to the position",
                height=100
            )
            
            special_instructions = st.text_input(
                "Any special instructions for your resume?",
                placeholder="e.g., 'Emphasize leadership experience' or 'Keep to one page'"
            )
            
            submitted = st.form_submit_button("✨ Generate Resume")
    
    # -------------------- Handle Submission -------------------- #
    if submitted:
        if not name or not email or not phone or not target_job:
            st.error("Please fill in all required fields (*)")
        else:
            with st.spinner("🔍 Crafting your professional resume..."):
                user_inputs = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "portfolio": portfolio,
                    "target_job": target_job,
                    "education": education,
                    "experience": experience,
                    "skills": skills,
                    "additional_info": additional_info,
                    "job_description": job_description,
                    "special_instructions": special_instructions
                }
                
                try:
                    resume = generate_resume(user_inputs)
                    st.success("✅ Resume generated successfully!")
                    st.markdown("---")
                    st.subheader("Your Professional Resume")
                    st.markdown(resume, unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Download as Word",
                        data=create_docx(resume),
                        file_name="My_Resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Error generating resume: {str(e)}")

if __name__ == "__main__":
    main()
