import json
import os
import re

from datetime import date

from google import genai
from dotenv import load_dotenv

from utils.file_reader import read_file

load_dotenv()

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is missing. "
        "Add your Gemini API key to the .env file."
    )

client = genai.Client(
    api_key=API_KEY
)

JD_POSITIVE_KEYWORDS = [
    "job description",
    "job title",
    "position",
    "role",
    "responsibilities",
    "responsibility",
    "requirements",
    "required qualifications",
    "qualifications",
    "skills required",
    "technical skills",
    "experience required",
    "years of experience",
    "education requirements",
    "preferred qualifications",
    "preferred skills",
    "what you will do",
    "what you'll do",
    "what we are looking for",
    "about the role",
    "about the job",
    "employment",
    "location",
    "salary",
    "benefits",
    "job responsibilities",
    "key responsibilities",
]

JD_NEGATIVE_KEYWORDS = [
    "turnitin",
    "similarity report",
    "similarity index",
    "ai detection report",
    "ai writing detection",
    "assignment submission",
    "course assignment",
    "academic report",
    "laboratory report",
    "lab report",
    "research paper",
    "research report",
    "project report",
    "journal paper",
    "conference paper",
    "thesis",
    "dissertation",
    "plagiarism report",
]

RESUME_LIKE_KEYWORDS = [
    "resume",
    "curriculum vitae",
    "professional summary",
    "career objective",
    "education",
    "work experience",
    "professional experience",
    "projects",
    "certifications",
    "linkedin",
    "github",
]

def _normalize_document_text(text):

    return " ".join(
        str(text)
        .lower()
        .replace("\n", " ")
        .split()
    )

def _document_has_contact_info(text):

    has_email = bool(
        re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            str(text),
            flags=re.IGNORECASE,
        )
    )

    has_linkedin = (
        "linkedin.com" in str(text).lower()
    )

    has_github = (
        "github.com" in str(text).lower()
    )

    return (
        has_email
        or has_linkedin
        or has_github
    )

def validate_resume_for_jd(resume_file):

    if resume_file is None:

        return (
            False,
            "Please upload a resume file."
        )

    try:

        resume_text = read_file(
            resume_file
        )

    except Exception as exc:

        return (
            False,
            f"Could not read the resume file: {exc}"
        )

    if (
        not resume_text
        or not str(resume_text).strip()
    ):

        return (
            False,
            "The uploaded resume does not contain readable text."
        )

    normalized = _normalize_document_text(
        resume_text
    )

    negative_matches = [
        keyword
        for keyword in [
            "turnitin",
            "similarity report",
            "similarity index",
            "ai detection report",
            "plagiarism report",
            "assignment submission",
        ]
        if keyword in normalized
    ]

    if negative_matches:

        return (
            False,
            "The left document does not appear to be a proper resume. "
            "Please upload a resume."
        )

    positive_matches = [
        keyword
        for keyword in RESUME_LIKE_KEYWORDS
        if keyword in normalized
    ]

    has_contact = _document_has_contact_info(
        resume_text
    )

    if (
        len(positive_matches) >= 4
        and has_contact
    ):

        return True, ""

    if len(positive_matches) >= 6:

        return True, ""

    return (
        False,
        "The left document does not appear to be a proper resume. "
        "Please upload a resume containing education, experience, "
        "skills, projects, certifications, or professional details."
    )

def validate_job_description_document(jd_file):

    if jd_file is None:

        return (
            False,
            "Please upload a job description file."
        )

    try:

        jd_text = read_file(
            jd_file
        )

    except Exception as exc:

        return (
            False,
            f"Could not read the job description file: {exc}"
        )

    if (
        not jd_text
        or not str(jd_text).strip()
    ):

        return (
            False,
            "The uploaded job description does not contain readable text."
        )

    normalized = _normalize_document_text(
        jd_text
    )

    negative_matches = [
        keyword
        for keyword in JD_NEGATIVE_KEYWORDS
        if keyword in normalized
    ]

    if len(negative_matches) >= 2:

        return (
            False,
            "The right document appears to be an academic/report/"
            "submission document rather than a job description. "
            "Please upload a proper job description."
        )

    resume_matches = [
        keyword
        for keyword in RESUME_LIKE_KEYWORDS
        if keyword in normalized
    ]

    if (
        len(resume_matches) >= 5
        and "responsibilities" not in normalized
        and "requirements" not in normalized
        and "qualifications" not in normalized
    ):

        return (
            False,
            "The right document appears to be a resume rather "
            "than a job description. Please upload a proper JD."
        )

    positive_matches = [
        keyword
        for keyword in JD_POSITIVE_KEYWORDS
        if keyword in normalized
    ]

    if len(positive_matches) >= 3:

        return True, ""

    strong_jd_signals = [
        "responsibilities",
        "requirements",
        "qualifications",
        "job description",
        "about the role",
        "years of experience",
        "skills required",
    ]

    strong_signal_count = sum(
        signal in normalized
        for signal in strong_jd_signals
    )

    if strong_signal_count >= 2:

        return True, ""

    return (
        False,
        "The right document does not appear to be a proper "
        "job description. Please upload a JD containing the "
        "role, responsibilities, requirements, qualifications, "
        "skills, or similar job-related information."
    )

def _extract_json(text):

    cleaned = (
        text or ""
    ).strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if (
        start == -1
        or end == -1
        or end <= start
    ):

        raise ValueError(
            "Gemini returned an invalid JSON response."
        )

    return json.loads(
        cleaned[
            start:end + 1
        ]
    )

def compare_resume_with_jd(
    resume_file,
    jd_file,
):

    resume_valid, resume_message = (
        validate_resume_for_jd(
            resume_file
        )
    )

    if not resume_valid:

        raise ValueError(
            resume_message
        )

    jd_valid, jd_message = (
        validate_job_description_document(
            jd_file
        )
    )

    if not jd_valid:

        raise ValueError(
            jd_message
        )

    resume_text = read_file(
        resume_file
    )

    jd_text = read_file(
        jd_file
    )

    if (
        not resume_text
        or not str(resume_text).strip()
    ):

        raise ValueError(
            "Could not extract readable text from the resume."
        )

    if (
        not jd_text
        or not str(jd_text).strip()
    ):

        raise ValueError(
            "Could not extract readable text from the job description."
        )

    today = date.today()

    prompt = f"""
You are an expert ATS Resume Reviewer and Job Matching Analyst.

Today's date is: {today}

Compare the following validated Resume with the validated
Job Description.

================ RESUME ================

{resume_text}

================ JOB DESCRIPTION ================

{jd_text}

=================================================

Analyze the resume strictly against the job description.

Consider:

- Required technical skills
- Programming languages
- Tools and technologies
- Education requirements
- Experience requirements
- Domain knowledge
- Professional skills
- Soft skills
- Job-specific qualifications

IMPORTANT:

Only identify a skill as matched if it is clearly supported
by BOTH the resume and job description.

Only identify a skill as missing if it is clearly required
or strongly expected from the job description and is not
clearly present in the resume.

Do NOT invent skills, qualifications, experience,
certifications, or achievements.

=================================================
MISSING SKILL CATEGORIZATION
=================================================

Categorize missing skills into:

1. technical_skills

Use for:
- Programming languages
- Software
- Frameworks
- Libraries
- Databases
- Platforms
- Tools
- Technical technologies
- Technical methodologies

2. domain_professional_skills

Use for:
- Domain-specific knowledge
- Industry knowledge
- Business knowledge
- Professional qualifications
- Job-specific knowledge

3. soft_skills

Use for:
- Communication
- Leadership
- Teamwork
- Collaboration
- Problem solving
- Stakeholder management
- Time management
- Adaptability
- Other interpersonal skills

If a category has no important missing skills,
return an empty array.

=================================================
MATCH SCORE
=================================================

Calculate match_score from 0 to 100.

80-100 = Strong Match
60-79  = Good Match
40-59  = Partial Match
0-39   = Low Match

The score must reflect the actual alignment between
the resume and the job description.

=================================================
RETURN FORMAT
=================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "match_score": 0,
    "matched_skills": [],
    "missing_skills": {{
        "technical_skills": [],
        "domain_professional_skills": [],
        "soft_skills": []
    }},
    "recommendations": [],
    "recruiter_summary": {{
        "top_strengths": [],
        "key_gaps": []
    }}
}}

=================================================
RULES
=================================================

1. match_score must be an integer from 0 to 100.

2. matched_skills must contain only skills clearly
supported by BOTH the resume and job description.

3. missing_skills must contain important requirements
from the job description that are not clearly present
in the resume.

4. Categorize missing skills accurately.

5. Keep each missing skill concise.

6. Do not put the same skill in both matched_skills
and missing_skills.

7. recommendations must provide practical suggestions
specifically for improving this resume for this job.

8. top_strengths should contain the strongest 1-3
areas of alignment.

9. key_gaps should contain the most important 1-3 gaps.

10. If there are genuinely no important gaps,
key_gaps may contain:
"No major skill gaps identified"

11. Do not invent missing requirements that are not
supported by the job description.

12. Do not return markdown.

13. Do not return ```json.

14. Return only the JSON object.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

    except Exception as exc:

        error_message = str(exc)

        if (
            "503" in error_message
            or "UNAVAILABLE" in error_message
        ):

            raise RuntimeError(
                "Gemini is temporarily experiencing high demand. "
                "Please wait a few seconds and try again."
            ) from exc

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
            or "quota" in error_message.lower()
        ):

            raise RuntimeError(
                "Gemini API quota has been exhausted. "
                "Please wait for the quota to reset or "
                "check your Gemini API usage and billing limits."
            ) from exc

        raise RuntimeError(
            f"Gemini API error: {error_message}"
        ) from exc

    try:

        response_text = getattr(
            response,
            "text",
            None,
        )

        if not response_text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        data = _extract_json(
            response_text
        )

    except (
        ValueError,
        json.JSONDecodeError,
    ) as exc:

        raise RuntimeError(
            "Gemini returned an invalid JSON response. "
            "Please try again."
        ) from exc

    try:

        score = int(
            data.get(
                "match_score",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        score = 0

    data["match_score"] = max(
        0,
        min(
            100,
            score,
        ),
    )

    if not isinstance(
        data.get("matched_skills"),
        list,
    ):

        data["matched_skills"] = []

    data["matched_skills"] = [
        str(skill).strip()
        for skill in data["matched_skills"]
        if str(skill).strip()
    ]

    missing = data.get(
        "missing_skills",
        {},
    )

    if not isinstance(
        missing,
        dict,
    ):

        missing = {}

    for category in [
        "technical_skills",
        "domain_professional_skills",
        "soft_skills",
    ]:

        if not isinstance(
            missing.get(category),
            list,
        ):

            missing[category] = []

        missing[category] = [
            str(skill).strip()
            for skill in missing[category]
            if str(skill).strip()
        ]

    data["missing_skills"] = missing

    if not isinstance(
        data.get("recommendations"),
        list,
    ):

        data["recommendations"] = []

    data["recommendations"] = [
        str(item).strip()
        for item in data["recommendations"]
        if str(item).strip()
    ]

    summary = data.get(
        "recruiter_summary",
        {},
    )

    if not isinstance(
        summary,
        dict,
    ):

        summary = {}

    top_strengths = summary.get(
        "top_strengths",
        [],
    )

    key_gaps = summary.get(
        "key_gaps",
        [],
    )

    if not isinstance(
        top_strengths,
        list,
    ):

        top_strengths = []

    if not isinstance(
        key_gaps,
        list,
    ):

        key_gaps = []

    top_strengths = [
        str(item).strip()
        for item in top_strengths
        if str(item).strip()
    ]

    key_gaps = [
        str(item).strip()
        for item in key_gaps
        if str(item).strip()
    ]

    all_missing = []

    for category in [
        "technical_skills",
        "domain_professional_skills",
        "soft_skills",
    ]:

        all_missing.extend(
            missing[category]
        )

    if data["match_score"] < 40:

        if all_missing:

            key_gaps = all_missing[:3]

        elif not key_gaps:

            key_gaps = [
                "The resume has limited alignment "
                "with the main requirements of this job."
            ]

    elif data["match_score"] < 60:

        if all_missing:

            key_gaps = all_missing[:3]

        elif not key_gaps:

            key_gaps = [
                "Some important job requirements are "
                "not strongly demonstrated in the resume."
            ]

    elif data["match_score"] < 80:

        if all_missing:

            key_gaps = all_missing[:3]

        elif not key_gaps:

            key_gaps = [
                "A few job-specific requirements could "
                "be highlighted more clearly."
            ]

    elif not key_gaps:

        key_gaps = [
            "No major skill gaps identified."
        ]

    if not top_strengths:

        if data["matched_skills"]:

            top_strengths = (
                data["matched_skills"][:3]
            )

        else:

            top_strengths = [
                "No strong direct skill matches identified."
            ]

    data["recruiter_summary"] = {
        "top_strengths": top_strengths[:3],
        "key_gaps": key_gaps[:3],
    }

    return data
