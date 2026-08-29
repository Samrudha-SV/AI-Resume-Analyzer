import json
import os
import re
import time

from google import genai
from dotenv import load_dotenv
from datetime import date

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
    api_key=API_KEY,
    http_options={"api_version": "v1"},
)

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
]

MAX_RETRIES_PER_MODEL = 2
RETRY_DELAYS = (1, 3)

RESUME_POSITIVE_KEYWORDS = [
    "resume",
    "curriculum vitae",
    "cv",
    "professional summary",
    "career objective",
    "objective",
    "education",
    "experience",
    "work experience",
    "professional experience",
    "skills",
    "technical skills",
    "projects",
    "project",
    "certifications",
    "certification",
    "internship",
    "internships",
    "achievements",
    "contact",
    "linkedin",
    "github",
]

RESUME_NEGATIVE_KEYWORDS = [
    "turnitin",
    "similarity report",
    "similarity index",
    "ai detection report",
    "ai writing detection",
    "assignment submission",
    "assignment report",
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
    "submission id",
    "student id",
]

def _normalize_document_text(text):
    return " ".join(
        str(text)
        .lower()
        .replace("\n", " ")
        .split()
    )

def validate_resume_document(resume_file):
    """
    Validate whether the uploaded document reasonably looks like
    a resume before sending it for ATS analysis.

    Returns:
        (True, "") for a valid-looking resume.

        (False, reason) for an invalid document.
    """

    if resume_file is None:
        return (
            False,
            "Please upload a resume file."
        )

    try:
        text = read_file(resume_file)
    except Exception as exc:
        return (
            False,
            f"Could not read the uploaded file: {exc}"
        )

    if not text or not str(text).strip():
        return (
            False,
            "The uploaded document does not contain readable text."
        )

    normalized = _normalize_document_text(text)

    filename = str(
        getattr(resume_file, "name", "")
    ).lower()

    negative_matches = [
        keyword
        for keyword in RESUME_NEGATIVE_KEYWORDS
        if keyword in normalized
    ]

    if len(negative_matches) >= 2:
        return (
            False,
            "The uploaded document appears to be an "
            "academic/report/submission document rather than a resume."
        )

    strong_negative_keywords = {
        "turnitin",
        "similarity report",
        "similarity index",
        "ai detection report",
        "plagiarism report",
        "assignment submission",
        "submission id",
    }

    if any(
        keyword in normalized
        for keyword in strong_negative_keywords
    ):
        return (
            False,
            "The uploaded document appears to be a report or "
            "submission document rather than a resume."
        )

    positive_matches = [
        keyword
        for keyword in RESUME_POSITIVE_KEYWORDS
        if keyword in normalized
    ]

    has_email = bool(
        re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            str(text),
            flags=re.IGNORECASE,
        )
    )

    has_phone = bool(
        re.search(
            r"(?:\+?\d[\d\s().-]{8,}\d)",
            str(text),
        )
    )

    has_linkedin = (
        "linkedin.com" in normalized
    )

    has_github = (
        "github.com" in normalized
    )

    contact_count = sum(
        [
            has_email,
            has_phone,
            has_linkedin,
            has_github,
        ]
    )

    filename_resume_signal = any(
        keyword in filename
        for keyword in [
            "resume",
            "cv",
            "curriculum",
            "profile",
        ]
    )

    if (
        len(positive_matches) >= 4
        and contact_count >= 1
    ):
        return True, ""

    if (
        len(positive_matches) >= 6
        and contact_count >= 0
    ):
        return True, ""

    if (
        filename_resume_signal
        and len(positive_matches) >= 3
    ):
        return True, ""

    return (
        False,
        "The uploaded document does not appear to be a proper "
        "resume. Please upload a resume containing information "
        "such as education, experience, skills, projects, "
        "certifications, or professional details."
    )

def _is_transient_error(message: str) -> bool:

    message = message.upper()

    return any(
        code in message
        for code in (
            "503",
            "500",
            "502",
            "504",
            "UNAVAILABLE",
            "INTERNAL",
        )
    )

def _is_quota_error(message: str) -> bool:

    message = message.upper()

    return any(
        code in message
        for code in (
            "429",
            "RESOURCE_EXHAUSTED",
            "QUOTA",
        )
    )

def _extract_json(text: str) -> dict:

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
            "Gemini did not return a JSON object."
        )

    return json.loads(
        cleaned[start:end + 1]
    )

def _normalize_result(data: dict) -> dict:

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini returned an invalid response structure."
        )

    try:
        score = int(
            data.get(
                "ats_score",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        score = 0

    def clean_list(value):

        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    score_breakdown = data.get(
        "score_breakdown",
        {},
    )

    if not isinstance(
        score_breakdown,
        dict,
    ):
        score_breakdown = {}

    def clean_score(value):

        try:
            return max(
                0,
                min(
                    100,
                    int(value),
                ),
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0

    return {
        "summary": str(
            data.get(
                "summary",
                "",
            )
        ).strip(),

        "skills": clean_list(
            data.get("skills")
        ),

        "strengths": clean_list(
            data.get("strengths")
        ),

        "weaknesses": clean_list(
            data.get("weaknesses")
        ),

        "ats_score": max(
            0,
            min(
                100,
                score,
            ),
        ),

        "suggestions": clean_list(
            data.get("suggestions")
        ),

        "score_breakdown": {
            "design": clean_score(
                score_breakdown.get(
                    "design",
                    0,
                )
            ),

            "structure": clean_score(
                score_breakdown.get(
                    "structure",
                    0,
                )
            ),

            "content": clean_score(
                score_breakdown.get(
                    "content",
                    0,
                )
            ),

            "grammar": clean_score(
                score_breakdown.get(
                    "grammar",
                    0,
                )
            ),

            "keywords": clean_score(
                score_breakdown.get(
                    "keywords",
                    0,
                )
            ),
        },
    }

def _generate(prompt: str):

    last_error = None

    for model in MODELS:

        for attempt in range(
            MAX_RETRIES_PER_MODEL
        ):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if not text:

                    raise RuntimeError(
                        f"Gemini returned an empty response "
                        f"using {model}."
                    )

                return text, model

            except Exception as exc:

                last_error = exc

                message = str(exc)

                if _is_quota_error(
                    message
                ):

                    raise RuntimeError(
                        "Gemini API quota/rate limit was reached. "
                        "Please wait for the quota window to reset "
                        "and try again."
                    ) from exc

                if _is_transient_error(
                    message
                ):

                    if (
                        attempt
                        < MAX_RETRIES_PER_MODEL - 1
                    ):

                        time.sleep(
                            RETRY_DELAYS[
                                attempt
                            ]
                        )

                        continue

                    break

                raise RuntimeError(
                    f"Gemini API error while using "
                    f"{model}: {message}"
                ) from exc

    raise RuntimeError(
        "Gemini is temporarily unavailable after retrying "
        "the available stable models. Please try again "
        "in a moment."
    ) from last_error

def analyze_resume(resume_file):

    if resume_file is None:

        raise ValueError(
            "Please upload a resume file first."
        )

    is_valid, validation_message = (
        validate_resume_document(
            resume_file
        )
    )

    if not is_valid:

        raise ValueError(
            validation_message
        )

    resume_text = read_file(
        resume_file
    )

    if (
        not resume_text
        or not str(resume_text).strip()
    ):

        raise ValueError(
            "Could not extract readable text from this document. "
            "Please upload a text-based resume file."
        )

    today = date.today()

    prompt = f"""
You are an expert ATS resume reviewer.

Today's date is: {today}

Analyze the resume below for a job seeker.

================ RESUME ================

{resume_text}

=========================================

Evaluate:

- Overall resume summary
- Technical and professional skills explicitly present
- Strong points supported by the resume
- Weaknesses or areas that could be improved
- ATS compatibility
- Practical resume improvement suggestions

IMPORTANT:

This document has already passed a resume-document
validation check.

Analyze ONLY the information explicitly present
in the resume.

Do not invent:
- skills
- experience
- qualifications
- certifications
- achievements
- projects

ATS SCORE RULES:

- Return an integer from 0 to 100.
- Score only the resume itself for ATS readability,
  structure, keyword quality, clarity, relevance,
  and completeness.

RETURN ONLY VALID JSON.

Use exactly this structure:

{{
    "summary": "",
    "skills": [],
    "strengths": [],
    "weaknesses": [],
    "ats_score": 0,
    "suggestions": [],
    "score_breakdown": {{
        "design": 0,
        "structure": 0,
        "content": 0,
        "grammar": 0,
        "keywords": 0
    }}
}}

SCORE BREAKDOWN:

design:
Visual readability, spacing, typography,
alignment, consistency, and presentation.

structure:
Organization of sections, headings,
ordering, hierarchy, and logical flow.

content:
Quality, relevance, completeness, clarity,
projects, experience, education, and achievements.

grammar:
Spelling, grammar, punctuation,
sentence clarity, and professional language.

keywords:
Relevant technical and professional
keywords present in the resume.

Each score must be an integer from 0 to 100.

The five breakdown scores are diagnostic scores.
They do not need to mathematically average exactly
to the overall ATS score.

Do not return markdown.
Do not return ```json fences.
Return only the JSON object.
"""

    last_parse_error = None

    for model in MODELS:

        for attempt in range(
            MAX_RETRIES_PER_MODEL
        ):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                response_text = getattr(
                    response,
                    "text",
                    None,
                )

                if not response_text:

                    raise RuntimeError(
                        f"Gemini returned an empty response "
                        f"using {model}."
                    )

                data = _extract_json(
                    response_text
                )

                return _normalize_result(
                    data
                )

            except ValueError as exc:

                last_parse_error = exc

                break

            except Exception as exc:

                message = str(exc)

                if _is_quota_error(
                    message
                ):

                    raise RuntimeError(
                        "Gemini API quota/rate limit was reached. "
                        "Please wait for the quota window to reset "
                        "and try again."
                    ) from exc

                if _is_transient_error(
                    message
                ):

                    last_parse_error = exc

                    if (
                        attempt
                        < MAX_RETRIES_PER_MODEL - 1
                    ):

                        time.sleep(
                            RETRY_DELAYS[
                                attempt
                            ]
                        )

                        continue

                    break

                raise RuntimeError(
                    f"Gemini API error while using "
                    f"{model}: {message}"
                ) from exc

    raise RuntimeError(
        "Gemini is temporarily unavailable or returned "
        "invalid data after trying the available stable "
        "models. Please try again in a moment."
    ) from last_parse_error
