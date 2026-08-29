import streamlit as st
import html

from services.resume_analyzer import (
    analyze_resume,
    validate_resume_document,
)
from services.jd_matcher import (
    compare_resume_with_jd,
    validate_resume_for_jd,
    validate_job_description_document,
)
from services.role_simulator import (
    simulate_roles,
    get_qualified_role_matches,
)

st.set_page_config(
    page_title = "AI Resume Analyzer | Gemini AI",
    page_icon ="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "resume_analysis_result" not in st.session_state:
    st.session_state.resume_analysis_result = None

if "jd_match_result" not in st.session_state:
    st.session_state.jd_match_result = None

if "jd_resume_name" not in st.session_state:
    st.session_state.jd_resume_name = None

if "jd_file_name" not in st.session_state:
    st.session_state.jd_file_name = None

if "resume_upload_version" not in st.session_state:
    st.session_state.resume_upload_version = 0

if "jd_upload_version" not in st.session_state:
    st.session_state.jd_upload_version = 0

with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html = True
    )

st.markdown(
    """
    <style>
    .st-key-analyze_resume_button .stButton > button,
    .st-key-new_resume_button .stButton > button {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 310px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.html(
    """
    <div class="app-brand">
        <div class="app-logo"> 🤖  </div>
        <div class="app-heading-area">
            <div class="app-title">
                <span class="title-dark">AI - Resume </span>
                <span class="title-gradient"> Analyzer</span>
            </div>

            <div class="app-subtitle">
                Intelligent Resume Intelligence &amp; Job Matching
            </div>

            <div class="app-description">
                AI-powered ATS Resume Analysis
                • Resume Review
                • Job Description Matching
            </div>
        </div>
    </div>
    """
)

st.divider()

def display_analysis_cards(
    title,
    items,
    card_class,
    section_key,
    count_label
):

    item_count = len(items)

    st.html(
        f"""
        <style>
        .st-key-{section_key}
        [data-testid="stExpander"] summary::after {{
            content: "{item_count} {count_label}";
            margin-left: auto;
            padding-left: 20px;
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
        }}
        </style>
        """
    )

    with st.container(
        key=section_key
    ):

        with st.expander(
            title
        ):

            if not items:
                st.info(
                    "No information was detected."
                )
                return

            for index, item in enumerate(
                items,
                start=1
            ):

                item_text = html.escape(
                    str(item)
                )

                st.html(
                    f"""
                    <div class="analysis-item-card {card_class}">

                        <div class="analysis-item-number">
                            {index:02d}
                        </div>

                        <div class="analysis-item-content">
                            {item_text}
                        </div>

                    </div>
                    """
                )

def display_skills(items):

    skill_count = len(items)

    st.html(
        f"""
        <style>
        .st-key-skills-section
        [data-testid="stExpander"] summary::after {{
            content: "{skill_count} detected";
            margin-left: auto;
            padding-left: 20px;
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
        }}
        </style>
        """
    )

    with st.container(
        key="skills-section"
    ):

        with st.expander(
            "🧩 Skills"
        ):

            if not items:
                st.info(
                    "No skills were detected in the resume."
                )
                return

            skills_html = ""

            for skill in items:

                skill_text = html.escape(
                    str(skill)
                )

                skills_html += f"""
                    <span class="resume-skill-chip">
                        {skill_text}
                    </span>
                """

            st.html(
                f"""
                <div class="resume-skills-container">
                    {skills_html}
                </div>
                """
            )

def show_upload_toast(file, session_key, message):
    if file is not None:
        file_signature = f"{file.name}_{file.size}"

        if st.session_state.get(session_key) != file_signature:
            st.session_state[session_key] = file_signature
            st.toast(message)

def get_recruiter_verdict(score):
    if score >= 80:
        return "Strong Match"
    elif score >= 60:
        return "Good Match with Minor Gaps"
    elif score >= 40:
        return "Partial Match — Skill Gaps Identified"
    else:
        return "Low Match — Major Gaps"

def generate_report(result):
    report = f"""
AI Resume Analysis Report
==================================
ATS Score: {result["ats_score"]}
----------------------------------
Summary:
{result["summary"]}
----------------------------------
Skills:
"""
    for skill in result.get("skills", []):
        report += f"\n• {skill}"

    report += "\n\n----------------------------------\n"
    report += "Strengths:\n"

    for strength in result.get("strengths", []):
        report += f"\n• {strength}"

    report += "\n\n----------------------------------\n"
    report += "Weaknesses:\n"

    for weakness in result.get("weaknesses", []):
        report += f"\n• {weakness}"

    report += "\n\n----------------------------------\n"
    report += "Suggestions:\n"

    for suggestion in result.get("suggestions", []):
        report += f"\n• {suggestion}"

    return report

def generate_jd_report(result):
    report = f"""
AI Resume vs Job Description Report

===================================

Match Score: {result["match_score"]}

-----------------------------------

Matched Skills:
"""

    for skill in result.get("matched_skills", []):
        report += f"\n• {skill}"

    report += "\n\n-----------------------------------\n"

    report += "Missing Skills:\n"

    report += "Missing Technical Skills:\n"

    for skill in result.get(
        "missing_technical_skills",
        []
    ):
        report += f"\n• {skill}"

    report += "\n\n-----------------------------------\n"

    report += "Missing Domain / Professional Skills:\n"

    for skill in result.get(
        "missing_domain_skills",
        []
    ):
        report += f"\n• {skill}"

    report += "\n\n-----------------------------------\n"

    report += "Missing Soft Skills:\n"

    for skill in result.get(
        "missing_soft_skills",
        []
    ):
        report += f"\n• {skill}"

    report += "\n\n-----------------------------------\n"

    report += "Recommendations:\n"

    for recommendation in result.get("recommendations", []):
        report += f"\n• {recommendation}"

    return report

st.markdown(
    """
    <style>

    /* Sidebar title row */
    section[data-testid="stSidebar"] .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }

    section[data-testid="stSidebar"] .sidebar-brand-icon {
        font-size: 26px;
        line-height: 1;
    }

    section[data-testid="stSidebar"] .sidebar-brand-title {
        color: #ffffff;
        font-family: "DM Sans", sans-serif;
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -0.4px;
    }

    /* Sidebar subtitle */
    section[data-testid="stSidebar"] .sidebar-brand-subtitle {
        color: #94a3b8;
        font-family: "DM Sans", sans-serif;
        font-size: 12px;
        margin-left: 36px;
        margin-top: -2px;
        margin-bottom: 22px;
    }

    /* Section labels */
    section[data-testid="stSidebar"] .sidebar-section-title {
        color: #ffffff;
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    /* About text */
    section[data-testid="stSidebar"] .sidebar-about {
        color: #c7d2e8;
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        line-height: 1.55;
        margin-bottom: 12px;
    }

    /* About capability rows */
    section[data-testid="stSidebar"] .sidebar-capability {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #dbe7ff;
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        line-height: 1.35;
        padding: 7px 0;
    }

    section[data-testid="stSidebar"] .sidebar-capability-icon {
        width: 22px;
        min-width: 22px;
        text-align: center;
        font-size: 16px;
    }

    /* Tool rows */
    section[data-testid="stSidebar"] .sidebar-feature {
        display: flex;
        align-items: center;
        gap: 11px;
        color: #dbe7ff;
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        line-height: 1.35;
        padding: 8px 10px;
        margin: 3px 0;
        border-radius: 8px;
        transition:
            background 0.15s ease,
            transform 0.15s ease;
    }

    section[data-testid="stSidebar"] .sidebar-feature:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] .sidebar-feature-icon {
        width: 22px;
        min-width: 22px;
        text-align: center;
        font-size: 17px;
    }

    /* Sidebar divider */
    section[data-testid="stSidebar"] .sidebar-divider {
        height: 1px;
        background: #263552;
        margin: 20px 0;
    }

    /* Sidebar footer */
    section[data-testid="stSidebar"] .sidebar-footer {
        color: #94a3b8;
        font-family: "DM Sans", sans-serif;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 24px;
        padding-top: 14px;
        border-top: 1px solid #263552;
    }

    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:

    st.html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">📄</div>
            <div class="sidebar-brand-title">Resume Tools</div>
        </div>

        <div class="sidebar-brand-subtitle">
            AI-powered career assistant
        </div>

        <div class="sidebar-divider"></div>

        <div class="sidebar-section-title">
            ℹ️ About
        </div>

        <div class="sidebar-about">
            AI Resume Analyzer helps job seekers improve and evaluate their resumes.
        </div>

        <div class="sidebar-capability">
            <div class="sidebar-capability-icon">📊</div>
            <div>Analyze ATS score</div>
        </div>

        <div class="sidebar-capability">
            <div class="sidebar-capability-icon">💪</div>
            <div>Find strengths &amp; weaknesses</div>
        </div>

        <div class="sidebar-capability">
            <div class="sidebar-capability-icon">💡</div>
            <div>Get resume improvement suggestions</div>
        </div>

        <div class="sidebar-capability">
            <div class="sidebar-capability-icon">🎯</div>
            <div>Compare resume with a Job Description</div>
        </div>

        <div class="sidebar-divider"></div>

        <div class="sidebar-section-title">
            🛠️ Tools
        </div>

        <div class="sidebar-feature">
            <div class="sidebar-feature-icon">📄</div>
            <div>ATS Resume Analysis</div>
        </div>

        <div class="sidebar-feature">
            <div class="sidebar-feature-icon">✨</div>
            <div>AI Resume Review</div>
        </div>

        <div class="sidebar-feature">
            <div class="sidebar-feature-icon">🎯</div>
            <div>Resume vs JD Matching</div>
        </div>

        <div class="sidebar-feature">
            <div class="sidebar-feature-icon">📥</div>
            <div>Download Reports</div>
        </div>

        <div class="sidebar-footer">
            Made with ❤️ using Streamlit &amp; Gemini AI
        </div>
        """
    )

tab1, tab2, tab3 = st.tabs([
    "📄 Resume Analysis",
    "🧭 Career Role Fit",
    "🎯 JD Match"
])

with tab1:

    uploaded_file = st.file_uploader(
        "Choose your Resume (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key=f"resume_analysis_{st.session_state.resume_upload_version}"
    )

    show_upload_toast(
        uploaded_file,
        "resume_analysis_upload",
        "📄 Resume uploaded successfully!"
    )

    action_col1, action_col2, action_col3 = st.columns(
        [0.22, 0.28, 0.50],
        gap="small"
    )

    with action_col1:

        analyze = st.button(
            "🤖 Analyze Resume",
            key="analyze_resume_button"
        )

    with action_col2:

        if st.session_state.resume_analysis_result is not None:

            if st.button(
                "🔄 Analyze Another Resume",
                key="new_resume_button"
            ):

                st.session_state.resume_analysis_result = None

                st.session_state.resume_upload_version += 1

                st.session_state.pop(
                    "resume_analysis_upload",
                    None
                )

                st.toast(
                    "📄 Ready for a new resume!",
                    icon="🔄"
                )

                st.rerun()

    if uploaded_file is not None and analyze:

        is_valid_resume, validation_message = (
            validate_resume_document(
                uploaded_file
            )
        )

        if not is_valid_resume:

            st.session_state.resume_analysis_result = None

            st.warning(
                "⚠️ **Invalid Resume File**\n\n"
                f"{validation_message}"
            )

        else:

            with st.spinner(
                "🔄 Analyzing your resume..."
            ):

                try:

                    result = analyze_resume(
                        uploaded_file
                    )

                    st.session_state.resume_analysis_result = result

                    st.toast(
                        "Resume analysis completed!",
                        icon="✅"
                    )

                    st.rerun()

                except Exception as e:

                    error_message = str(e)

                    if (
                        "503" in error_message
                        or "UNAVAILABLE" in error_message
                    ):

                        st.error(
                            "⚠️ Gemini is temporarily experiencing "
                            "high demand. Please wait a few seconds "
                            "and try again."
                        )

                    elif (
                        "429" in error_message
                        or "RESOURCE_EXHAUSTED" in error_message
                        or "quota" in error_message.lower()
                    ):

                        st.error(
                            "⚠️ Gemini API quota is currently unavailable. "
                            "Please wait for the quota to reset and try again."
                        )

                    else:

                        st.error(
                            f"⚠️ Unable to analyze the resume: "
                            f"{error_message}"
                        )

    if st.session_state.resume_analysis_result is not None:

        result = st.session_state.resume_analysis_result

        score = result["ats_score"]

        if score >= 80:

            score_status = "Excellent"

        elif score >= 60:

            score_status = "Good"

        elif score >= 40:

            score_status = "Needs Improvement"

        else:

            score_status = "Needs Major Improvement"

        col1, col2 = st.columns(
            [2, 3],
            gap="large"
        )

        with col1:

            if score >= 80:
                score_status = "Excellent"
            elif score >= 60:
                score_status = "Good"
            elif score >= 40:
                score_status = "Needs Improvement"
            else:
                score_status = "Needs Major Improvement"

            if score >= 80:
                ring_color = "#22c55e"
            elif score >= 60:
                ring_color = "#f59e0b"
            elif score >= 40:
                ring_color = "#eab308"
            else:
                ring_color = "#ef4444"

            score_angle = max(
                0,
                min(
                    360,
                    float(score) * 3.6
                )
            )

            with st.container(
                key="ats-result-card"
            ):

                st.html(
                    f"""
                    <div class="ats-card-content">

                        <div class="ats-label">
                            ATS COMPATIBILITY SCORE
                        </div>

                        <div class="ats-circle-wrapper">

                            <div
                                class="ats-circle"
                                style="
                                    background:
                                    conic-gradient(
                                        {ring_color} 0deg,
                                        {ring_color} {score_angle}deg,
                                    );
                                "
                            >

                                <div class="ats-circle-inner">

                                    <div class="ats-circle-number">
                                        {score}
                                    </div>

                                    <div class="ats-circle-total">
                                        /100
                                    </div>

                                </div>

                            </div>

                        </div>

                        <div
                            class="ats-status"
                            style="color: {ring_color};"
                        >
                            {score_status}
                        </div>

                    </div>
                    """
                )

        with col2:

            summary = html.escape(
                str(
                    result.get(
                        "summary",
                        ""
                    )
                )
            )

            st.html(
                f"""
                <div class="overview-card">

                    <div class="overview-title">
                        📄 RESUME OVERVIEW
                    </div>

                    <div class="overview-content">
                        {summary}
                    </div>

                </div>
                """
            )

        st.markdown(
            '<div class="results-section">',
            unsafe_allow_html=True
        )

        display_skills(
            result.get("skills", [])
        )

        display_analysis_cards(
            "✨ Strengths",
            result.get("strengths", []),
            "strength-card",
            "strengths-section",
            "highlights"
        )

        display_analysis_cards(
            "🎯 Areas to Improve",
            result.get("weaknesses", []),
            "weakness-card",
            "improvement-section",
            "areas"
        )

        display_analysis_cards(
            "💡 AI Suggestions",
            result.get("suggestions", []),
            "suggestion-card",
            "suggestions-section",
            "actions"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        report = generate_report(
            result
        )

        download_col1, download_col2, download_col3 = st.columns(
            [1, 1.4, 1]
        )

        with download_col2:

            st.download_button(
                label="📥 Download Resume Analysis Report",
                data=report,
                file_name="Resume_Analysis_Report.txt",
                mime="text/plain",
                use_container_width=True
            )

            st.divider()

with tab2:

    st.header("🧭 Career Role Fit")

    st.html(
        """
        <div class="role-simulator-intro">

            <div class="role-simulator-intro-title">
                🧭 Discover Which Career Roles Fit Your Resume
            </div>

            <div class="role-simulator-intro-text">
                See your top career matches based on the skills
                detected in your resume, or explore any supported
                career role to check your fit.
            </div>

        </div>
        """
    )

    if (
        st.session_state.resume_analysis_result
        is None
    ):

        st.info(
            "📄 Please go to the "
            "**Resume Analysis** tab, upload your resume, "
            "and click **Analyze Resume** first."
        )

    else:

        resume_result = (
            st.session_state.resume_analysis_result
        )

        resume_skills = resume_result.get(
            "skills",
            []
        )

        if not resume_skills:

            st.warning(
                "⚠️ No skills were detected from the "
                "analyzed resume. Please try analyzing "
                "the resume again."
            )

        else:

            role_results = simulate_roles(
                resume_skills
            )

            qualified_roles = get_qualified_role_matches(
                role_results,
                minimum_score=40
            )

            if not qualified_roles:

                st.warning(
                    "⚠️ **No suitable career role found**\n\n"
                    "The skills detected in this resume do not currently have enough "
                    "overlap with the supported career-role profiles. The automatic "
                    "career matches have therefore not been displayed."
                )

            else:

                top_three_roles = qualified_roles[:3]

                st.markdown(
                    "### 🏆 Top Career Matches"
                )

                st.caption(
                    "Only roles with a meaningful skill overlap and a Role Fit Score "
                    "of at least 40/100 are shown."
                )

                top_columns = st.columns(
                    3,
                    gap="large"
                )

                for index, role_data in enumerate(
                    top_three_roles
                ):

                    score = role_data["score"]

                    if score >= 80:

                        status = "Strong Fit"

                    elif score >= 60:

                        status = "Good Fit"

                    elif score >= 40:

                        status = "Develop Skills"

                    else:

                        status = "Large Skill Gap"

                    rank = index + 1

                    if rank == 1:

                        rank_icon = "🥇"

                    elif rank == 2:

                        rank_icon = "🥈"

                    else:

                        rank_icon = "🥉"

                    with top_columns[index]:

                        st.html(
                            f"""
                            <div class="top3-role-card rank-{rank}">

                                <div class="top3-rank">
                                    {rank_icon}
                                    <span>#{rank} MATCH</span>
                                </div>

                                <div class="top3-role-header">

                                    <div class="top3-role-icon">
                                        {role_data["icon"]}
                                    </div>

                                    <div class="top3-role-name">
                                        {html.escape(
                                            str(
                                                role_data["role"]
                                            )
                                        )}
                                    </div>

                                </div>

                                <div class="top3-score">

                                    {score}

                                    <span>
                                        /100
                                    </span>

                                </div>

                                <div class="top3-score-label">
                                    Role Fit Score
                                </div>

                                <div class="top3-progress">

                                    <div
                                        class="top3-progress-fill"
                                        style="width:{score}%"
                                    ></div>

                                </div>

                                <div class="top3-status">
                                    {status}
                                </div>

                                <div class="top3-description">
                                    {html.escape(
                                        str(
                                            role_data[
                                                "description"
                                            ]
                                        )
                                    )}
                                </div>

                            </div>
                            """
                        )

            st.markdown("---")

            st.markdown(
                "### 🔎 Explore Any Career Role"
            )

            st.caption(
                "Select a supported role from the list, "
                "or type the role you want to check."
            )

            role_options = [

                item["role"]

                for item in role_results

            ]

            selected_role = st.selectbox(

                "Career role",

                options=role_options,

                index=None,

                placeholder=(
                    "🔎 Search or select a career role..."
                ),

                accept_new_options=True,

                key="career_role_search",

                label_visibility="collapsed"

            )

            if selected_role is None:

                st.info(
                    "💡 Start typing a role or open the "
                    "dropdown to choose from the supported "
                    "career roles."
                )

            else:

                selected_role_text = str(
                    selected_role
                ).strip()

                selected_role_data = None

                for role_data in role_results:

                    if (
                        role_data["role"].strip().lower()
                        == selected_role_text.lower()
                    ):

                        selected_role_data = role_data

                        break

                if selected_role_data is not None:

                    selected_score = (
                        selected_role_data["score"]
                    )

                    if selected_score >= 80:

                        selected_status = "Strong Fit"

                    elif selected_score >= 60:

                        selected_status = "Good Fit"

                    elif selected_score >= 40:

                        selected_status = "Develop Skills"

                    else:

                        selected_status = "Large Skill Gap"

                    matched_skills = (
                        selected_role_data.get(
                            "matched",
                            []
                        )
                    )

                    missing_skills = (
                        selected_role_data.get(
                            "missing",
                            []
                        )
                    )

                    matched_html = ""

                    for skill in matched_skills:

                        safe_skill = html.escape(
                            str(skill)
                        )

                        matched_html += f"""
                        <div class="category-skill matched-skill">
                            <span class="category-skill-icon">
                                ✓
                            </span>

                            <span class="clean-missing-text">
                                {safe_skill}
                            </span>
                        </div>
                        """

                    if not matched_html:

                        matched_html = """
                        <div class="category-empty">
                            No matched skills found.
                        </div>
                        """

                    missing_html = ""

                    for skill in missing_skills[:8]:

                        missing_html += f"""
                        <span class="role-skill-chip missing">
                            {html.escape(
                                str(skill)
                            )}
                        </span>
                        """

                    if not missing_html:

                        missing_html = """
                        <span class="role-skill-chip">
                            No major skill gaps detected
                        </span>
                        """

                    st.html(
                        f"""
                        <div class="role-detail-card">

                            <div class="selected-role-heading">

                                <div class="selected-role-icon">
                                    {selected_role_data["icon"]}
                                </div>

                                <div>

                                    <div class="selected-role-title">
                                        {html.escape(
                                            str(
                                                selected_role_data[
                                                    "role"
                                                ]
                                            )
                                        )}
                                    </div>

                                    <div class="selected-role-status">
                                        {selected_status}
                                    </div>

                                </div>

                            </div>

                            <div class="selected-role-score">

                                {selected_score}

                                <span>
                                    /100 Role Fit Score
                                </span>

                            </div>

                            <div class="selected-role-bar">

                                <div
                                    class="selected-role-bar-fill"
                                    style="
                                        width:
                                        {selected_score}%;
                                    "
                                ></div>

                            </div>

                            <div class="role-detail-section">

                                SKILLS YOU ALREADY HAVE

                            </div>

                            <div class="role-skill-list">

                                {matched_html}

                            </div>

                            <div class="role-detail-section">

                                SKILLS YOU SHOULD DEVELOP

                            </div>

                            <div class="role-skill-list">

                                {missing_html}

                            </div>

                            <div class="role-note">

                                💡

                                <strong>
                                    How to interpret this:
                                </strong>

                                Your Role Fit Score reflects
                                how much of this role's weighted
                                skill profile is represented
                                in your resume.

                                It is a guidance indicator,
                                not a prediction of hiring
                                success.

                            </div>

                        </div>
                        """
                    )

                else:

                    st.info(
                        f"💡 **{selected_role_text}** isn't in our career library yet. "
                        "Try another role from the list — we're continuously adding "
                        "more career paths!"
                    )

with tab3:

    st.header("🎯 Resume vs Job Description")

    upload_col1, upload_col2 = st.columns(
        [1, 1],
        gap="large"
    )

    with upload_col1:

        resume_file = st.file_uploader(
            "📄 Upload Resume",
            type=["pdf", "docx", "txt"],
            key=f"resume_match_{st.session_state.jd_upload_version}"
        )

        show_upload_toast(
            resume_file,
            "jd_resume_upload",
            "📄 Resume uploaded successfully!"
        )

    with upload_col2:

        jd_file = st.file_uploader(
            "📋 Upload Job Description",
            type=["pdf", "docx", "txt"],
            key=f"jd_match_{st.session_state.jd_upload_version}"
        )

        show_upload_toast(
            jd_file,
            "jd_file_upload",
            "📋 Job Description uploaded successfully!"
        )

    compare_col1, compare_col2, compare_col3 = st.columns(
        [1, 1.2, 1]
    )

    with compare_col2:

        compare = st.button(
            "🎯 Compare Resume with JD",
            use_container_width=True
        )

    if (
        resume_file
        and jd_file
        and compare
    ):

        resume_valid, resume_message = (
            validate_resume_for_jd(
                resume_file
            )
        )

        if not resume_valid:

            st.session_state.jd_match_result = None

            st.warning(
                "⚠️ **Invalid Resume File**\n\n"
                f"{resume_message}"
            )

        else:

            jd_valid, jd_message = (
                validate_job_description_document(
                    jd_file
                )
            )

            if not jd_valid:

                st.session_state.jd_match_result = None

                st.warning(
                    "⚠️ **Invalid Job Description File**\n\n"
                    f"{jd_message}"
                )

            else:

                st.session_state.jd_match_result = None

                with st.spinner(
                    "🔄 Comparing Resume with Job Description..."
                ):

                    try:

                        result = compare_resume_with_jd(
                            resume_file,
                            jd_file
                        )

                        st.session_state.jd_match_result = result

                        st.session_state.jd_resume_name = (
                            resume_file.name
                        )

                        st.session_state.jd_file_name = (
                            jd_file.name
                        )

                        st.toast(
                            "✅ JD matching completed!",
                            icon="✅"
                        )

                    except Exception as e:

                        error_message = str(e)

                        if (
                            "503" in error_message
                            or "UNAVAILABLE" in error_message
                        ):

                            st.error(
                                "⚠️ Gemini is temporarily experiencing "
                                "high demand. Please wait a few seconds "
                                "and try again."
                            )

                        elif (
                            "429" in error_message
                            or "RESOURCE_EXHAUSTED" in error_message
                            or "quota" in error_message.lower()
                        ):

                            st.error(
                                "⚠️ Gemini API quota is currently unavailable. "
                                "Please wait for the quota to reset and try again."
                            )

                        else:

                            st.error(
                                f"⚠️ JD Matching Error: "
                                f"{error_message}"
                            )

    if st.session_state.jd_match_result is not None:

        new_jd_col1, new_jd_col2, new_jd_col3 = st.columns(
            [1, 1.2, 1]
        )

        with new_jd_col2:

            if st.button(
                "🔄 Start New Comparison",
                use_container_width=True,
                key="new_jd_button"
            ):

                st.session_state.jd_match_result = None

                st.session_state.jd_resume_name = None

                st.session_state.jd_file_name = None

                st.session_state.jd_upload_version += 1

                st.session_state.pop(
                    "jd_resume_upload",
                    None
                )

                st.session_state.pop(
                    "jd_file_upload",
                    None
                )

                st.toast(
                    "📄 Ready for a new Resume & Job Description!",
                    icon="🔄"
                )

                st.rerun()

    if st.session_state.jd_match_result is not None:

        result = st.session_state.jd_match_result

        missing_skills = result.get(
            "missing_skills",
            {}
        )

        if isinstance(missing_skills, dict):

            technical_skills = missing_skills.get(
                "technical_skills",
                []
            )

            domain_skills = missing_skills.get(
                "domain_professional_skills",
                []
            )

            soft_skills = missing_skills.get(
                "soft_skills",
                []
            )

        elif isinstance(missing_skills, list):

            technical_skills = missing_skills
            domain_skills = []
            soft_skills = []

        else:

            technical_skills = []
            domain_skills = []
            soft_skills = []

        result["missing_technical_skills"] = technical_skills
        result["missing_domain_skills"] = domain_skills
        result["missing_soft_skills"] = soft_skills

        score = result["match_score"]

        if score >= 80:

            score_status = "Excellent Match"

        elif score >= 60:

            score_status = "Good Match"

        elif score >= 40:

            score_status = "Moderate Match"

        else:

            score_status = "Low Match"

        st.html(
            f"""
            <div class="ats-score-card">

                <div class="ats-label">
                    JOB DESCRIPTION MATCH SCORE
                </div>

                <div class="ats-score">
                    {score}<span>/100</span>
                </div>

                <div class="ats-status">
                    {score_status}
                </div>

                <div class="ats-bar">

                    <div
                        class="ats-bar-fill"
                        style="width:{score}%"
                    ></div>

                </div>

                <div class="ats-description">
                    How closely your resume matches
                    the requirements of this job description.
                </div>

            </div>
            """
        )

        verdict = get_recruiter_verdict(score)

        matched_skills = result.get(
            "matched_skills",
            []
        )

        technical_skills = result.get(
            "missing_technical_skills",
            []
        )

        domain_skills = result.get(
            "missing_domain_skills",
            []
        )

        soft_skills = result.get(
            "missing_soft_skills",
            []
        )

        all_missing_skills = (
            technical_skills
            + domain_skills
            + soft_skills
        )

        top_strengths = matched_skills[:2]

        top_gaps = all_missing_skills[:2]

        strengths_html = ""

        if top_strengths:

            for skill in top_strengths:

                strengths_html += f"""
                <div class="recruiter-item">

                    <span class="recruiter-icon">
                        ✓
                    </span>

                    <span>
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

        else:

            strengths_html = """
            <div class="recruiter-item">

                <span class="recruiter-icon">
                    ✓
                </span>

                <span>
                    No major strengths identified
                </span>

            </div>
            """

        gaps_html = ""

        if top_gaps:

            for skill in top_gaps:

                gaps_html += f"""
                <div class="recruiter-item">

                    <span class="recruiter-icon">
                        !
                    </span>

                    <span>
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

        else:

            gaps_html = """
            <div class="recruiter-item">

                <span class="recruiter-icon">
                    !
                </span>

                <span>
                    No major skill gaps identified
                </span>

            </div>
            """

        st.html(
            f"""
            <div class="recruiter-summary-card">

                <div class="recruiter-summary-title">
                    <span>🎯</span>
                    ROLE FIT SNAPSHOT
                </div>

                <div class="recruiter-summary-grid">

                    <div class="recruiter-column">

                        <div class="recruiter-column-title">
                            ✅ TOP STRENGTHS
                        </div>

                        <div class="recruiter-list">
                            {strengths_html}
                        </div>

                    </div>

                    <div class="recruiter-column">

                        <div class="recruiter-column-title">
                            ⚠️ KEY GAPS
                        </div>

                        <div class="recruiter-list">
                            {gaps_html}
                        </div>

                    </div>

                </div>

                <div class="recruiter-verdict">

                    <div class="recruiter-column-title">
                        🎯 VERDICT
                    </div>

                    <div class="recruiter-verdict-text">
                        {verdict}
                    </div>

                </div>

            </div>
            """
        )

        col1, col2 = st.columns(
            [0.8, 1.12],
            gap="large"
        )

        with col1:

            matched_html = ""

            for skill in matched_skills:

                matched_html += f"""
                <div class="skill-item matched-skill">

                    <span class="skill-icon">
                        ✓
                    </span>

                    <span>
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

            if not matched_html:

                matched_html = """
                <div class="category-empty">
                    No matched skills found.
                </div>
                """

            st.html(
                f"""
                <div class="skills-card">

                    <div class="skills-title matched-title">

                        <span>✅</span>

                        MATCHED SKILLS

                    </div>

                    <div class="skills-list">

                        {matched_html}

                    </div>

                </div>
                """
            )

        with col2:

            technical_html = ""

            for skill in technical_skills:

                technical_html += f"""
                <div class="category-skill">

                    <span class="category-skill-icon">
                        🛠️
                    </span>

                    <span class="clean-missing-text">
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

            if not technical_html:

                technical_html = """
                <div class="category-empty">
                    No major technical gaps identified.
                </div>
                """

            domain_html = ""

            for skill in domain_skills:

                domain_html += f"""
                <div class="category-skill">

                    <span class="category-skill-icon">
                        📊
                    </span>

                    <span class="clean-missing-text">
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

            if not domain_html:

                domain_html = """
                <div class="category-empty">
                    No major domain or professional gaps identified.
                </div>
                """

            soft_html = ""

            for skill in soft_skills:

                soft_html += f"""
                <div class="category-skill">

                    <span class="category-skill-icon">
                        🤝
                    </span>

                    <span class="clean-missing-text">
                        {html.escape(str(skill))}
                    </span>

                </div>
                """

            if not soft_html:

                soft_html = """
                <div class="category-empty">
                    No major soft-skill gaps identified.
                </div>
                """

            st.html(
                f"""
                <div class="clean-missing-card">

                    <div class="clean-missing-header">

                        <span class="clean-missing-header-icon">
                            ❌
                        </span>

                        <span>
                            MISSING SKILLS
                        </span>

                    </div>

                    <div class="clean-missing-subtitle">

                        Important requirements from the job
                        description that are not clearly shown
                        in the resume.

                    </div>

                    <div class="missing-categories">

                        <div class="missing-category">

                            <div class="missing-category-title">
                                🛠️ TECHNICAL / TOOLS
                            </div>

                            <div class="category-skills">
                                {technical_html}
                            </div>

                        </div>

                        <div class="missing-category">

                            <div class="missing-category-title">
                                📊 DOMAIN / PROFESSIONAL
                            </div>

                            <div class="category-skills">
                                {domain_html}
                            </div>

                        </div>

                        <div class="missing-category">

                            <div class="missing-category-title">
                                🤝 SOFT SKILLS
                            </div>

                            <div class="category-skills">
                                {soft_html}
                            </div>

                        </div>

                    </div>

                </div>
                """
            )

        recommendations_html = ""

        for index, recommendation in enumerate(
            result["recommendations"],
            start=1
        ):

            recommendations_html += f"""
            <div class="recommendation-item">

                <div class="recommendation-number">
                    {index}
                </div>

                <div class="recommendation-text">
                    {html.escape(str(recommendation))}
                </div>

            </div>
            """

        st.html(
            f"""
            <div class="recommendations-wrapper">

                <div class="recommendations-card">

                    <div class="recommendations-title">

                        <span>💡</span>

                        AI RECOMMENDATIONS

                    </div>

                    <div class="recommendations-subtitle">

                        Practical suggestions to improve your
                        resume match

                    </div>

                    <div class="recommendations-list">

                        {recommendations_html}

                    </div>

                </div>

            </div>
            """
        )

        jd_report = generate_jd_report(
            result
        )

        download_left, download_center, download_right = st.columns(
            [1, 1, 1]
        )

        with download_center:

            st.download_button(
                label="📥 Download JD Match Report",
                data=jd_report,
                file_name="JD_Match_Report.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()

st.markdown(
    """
    <div style='text-align:center; color:gray; padding:10px;'>
        🤖 AI Resume Analyzer |
        Built with ❤️ using Streamlit & Google Gemini AI
    </div>
    """,
    unsafe_allow_html=True
)