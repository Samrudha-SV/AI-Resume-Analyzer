# 🤖 AI Resume Analyzer

An AI-powered resume analysis and job-matching application built with Python, Streamlit, and Google Gemini AI.

The application helps users evaluate their resumes, identify strengths and weaknesses, discover suitable career roles, and compare a resume against a specific job description.

## ✨ Features

### 📄 Resume Analysis

Upload a resume in PDF, DOCX, or TXT format and receive:

- ATS compatibility score
- Resume overview
- Detected skills
- Strengths
- Weaknesses
- AI-powered improvement suggestions

The application also validates uploaded documents and prevents non-resume documents from being analyzed as resumes.

### 🎯 Career Role Fit

Analyze the skills detected from a resume and identify suitable career roles.

The application provides:

- Top career-role matches
- Role-fit scores
- Skill-gap information
- Career-role descriptions
- Option to explore supported career roles manually

If the resume does not have sufficient overlap with the supported roles, the application clearly indicates that no suitable career role was found instead of displaying unrelated matches.

### 🎯 Resume vs Job Description Matching

Compare a resume against a specific job description.

The comparison provides:

- Job-description match score
- Matched skills
- Missing skills
- Technical/tool requirements
- Domain/professional requirements
- Soft-skill requirements
- Overall match verdict

The application also validates both uploaded documents to ensure that a proper resume and job description are provided.

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Google Gemini AI**
- **PyPDF**
- **python-docx**
- **python-dotenv**
- **HTML/CSS**
- **Git/GitHub**

## 🏗️ Project Structure

```text
AI Resume Analyzer Project/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env
│
├── assets/
│   └── style.css
│
├── prompts/
│
├── services/
│   ├── __init__.py
│   ├── resume_analyzer.py
│   ├── jd_matcher.py
│   └── role_simulator.py
│
├── utils/
│   ├── __init__.py
│   └── file_reader.py
│
├── uploads/
├── reports/
└── resumes/