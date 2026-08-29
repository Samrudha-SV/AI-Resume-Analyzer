import re

ROLE_DEFINITIONS = {

    "Software Engineer": {

        "icon": "💻",

        "description":
            "Develops software applications, programs, APIs, "
            "and automation solutions.",

        "skills": {

            "python": 1.0,
            "java": 1.0,
            "c++": 0.9,
            "c": 0.8,

            "sql": 0.8,

            "data structures": 1.0,
            "algorithms": 1.0,
            "oops": 0.8,

            "git": 0.7,
            "github": 0.5,

            "rest api": 0.9,
            "api": 0.7,

            "testing": 0.5,
            "debugging": 0.6
        }
    },

    "Frontend Developer": {

        "icon": "🎨",

        "description":
            "Builds responsive and interactive web interfaces "
            "using modern frontend technologies.",

        "skills": {

            "html": 1.0,
            "css": 1.0,
            "javascript": 1.0,

            "react": 1.0,
            "angular": 0.9,
            "vue": 0.8,

            "typescript": 0.8,

            "bootstrap": 0.5,

            "responsive design": 0.8,
            "ui": 0.6,
            "ux": 0.5,

            "git": 0.6,
            "github": 0.5
        }
    },

    "Backend Developer": {

        "icon": "⚙️",

        "description":
            "Develops server-side applications, APIs, databases, "
            "and backend services.",

        "skills": {

            "python": 0.9,
            "java": 1.0,
            "c#": 0.9,
            "node.js": 0.9,

            "sql": 1.0,
            "mysql": 0.8,

            "rest api": 1.0,
            "api": 0.8,

            "spring boot": 1.0,
            "django": 0.9,
            "flask": 0.8,

            "backend": 1.0,

            "git": 0.6,
            "github": 0.5
        }
    },

    "Full Stack Developer": {

        "icon": "🌐",

        "description":
            "Develops both frontend interfaces and backend "
            "applications for web-based systems.",

        "skills": {

            "html": 0.8,
            "css": 0.8,
            "javascript": 1.0,

            "react": 0.9,
            "angular": 0.8,

            "python": 0.7,
            "java": 0.7,
            "node.js": 0.9,

            "sql": 0.8,

            "rest api": 0.9,
            "api": 0.7,

            "git": 0.6,
            "github": 0.5
        }
    },

    "QA / Test Automation Engineer": {

        "icon": "🧪",

        "description":
            "Tests software applications and develops automated "
            "testing solutions.",

        "skills": {

            "testing": 1.0,
            "automation": 1.0,

            "python": 0.8,
            "java": 0.8,

            "selenium": 1.0,
            "playwright": 0.9,

            "api testing": 1.0,
            "postman": 0.8,

            "sql": 0.7,

            "git": 0.6,
            "github": 0.5,

            "debugging": 0.7
        }
    },

    "Data Analyst": {

        "icon": "📊",

        "description":
            "Analyzes data and creates reports, dashboards, "
            "and business insights.",

        "skills": {

            "sql": 1.0,
            "python": 0.9,

            "excel": 0.9,
            "power bi": 1.0,
            "tableau": 1.0,

            "pandas": 0.9,
            "numpy": 0.7,

            "data analysis": 1.0,
            "statistics": 0.8,

            "data visualization": 0.9
        }
    },

    "AI / ML Engineer": {

        "icon": "🤖",

        "description":
            "Develops artificial intelligence and machine "
            "learning applications and models.",

        "skills": {

            "python": 1.0,

            "machine learning": 1.0,
            "deep learning": 1.0,

            "pandas": 0.8,
            "numpy": 0.8,

            "scikit-learn": 1.0,

            "tensorflow": 0.8,
            "pytorch": 0.8,

            "nlp": 0.8,

            "generative ai": 0.9,
            "llm": 0.8,

            "data analysis": 0.6
        }
    },

    "Cloud / DevOps Engineer": {

        "icon": "☁️",

        "description":
            "Works with cloud infrastructure, deployment, "
            "containers, automation, and CI/CD.",

        "skills": {

            "aws": 1.0,
            "azure": 0.9,
            "gcp": 0.9,

            "linux": 0.9,

            "docker": 1.0,
            "kubernetes": 1.0,

            "git": 0.8,
            "github": 0.6,

            "jenkins": 0.8,
            "ci/cd": 1.0,

            "terraform": 0.8,

            "python": 0.6,
            "bash": 0.6
        }
    },

    "Cybersecurity Analyst": {

        "icon": "🔐",

        "description":
            "Helps protect systems, networks, applications, "
            "and data from security threats.",

        "skills": {

            "cybersecurity": 1.0,
            "network security": 1.0,

            "networking": 0.9,
            "linux": 0.8,

            "ethical hacking": 1.0,
            "penetration testing": 1.0,

            "siem": 0.9,
            "wireshark": 0.8,

            "python": 0.6,

            "cryptography": 0.8,

            "firewall": 0.7
        }
    },

    "Embedded Engineer": {

        "icon": "🔧",

        "description":
            "Develops embedded software, firmware, "
            "microcontroller systems, and hardware interfaces.",

        "skills": {

            "c": 1.0,
            "c++": 1.0,

            "embedded systems": 1.0,
            "embedded": 1.0,

            "microcontroller": 1.0,
            "firmware": 1.0,

            "arduino": 0.8,
            "esp32": 0.8,
            "esp8266": 0.8,

            "iot": 0.8,
            "sensors": 0.7,

            "uart": 0.7,
            "spi": 0.7,
            "i2c": 0.7,

            "debugging": 0.6
        }
    },

    "IoT Engineer": {

        "icon": "📡",

        "description":
            "Builds connected devices and IoT systems using "
            "sensors, microcontrollers, networking, and cloud.",

        "skills": {

            "iot": 1.0,

            "arduino": 0.8,
            "esp8266": 0.8,
            "esp32": 0.8,

            "raspberry pi": 0.8,

            "sensors": 0.8,
            "embedded systems": 0.8,

            "mqtt": 1.0,
            "lorawan": 0.9,

            "python": 0.6,
            "c": 0.7,
            "c++": 0.7,

            "cloud": 0.7,

            "thingspeak": 0.6,
            "adafruit io": 0.6
        }
    },

    "VLSI / RTL Design Engineer": {

        "icon": "🔬",

        "description":
            "Designs and verifies digital hardware and RTL "
            "using HDL and semiconductor design concepts.",

        "skills": {

            "verilog": 1.0,
            "systemverilog": 1.0,

            "vlsi": 1.0,
            "rtl": 1.0,

            "digital electronics": 0.9,
            "digital design": 0.9,

            "cadence": 0.9,

            "asic": 0.8,
            "fpga": 0.8,

            "synthesis": 0.8,
            "verification": 0.9,

            "testbench": 0.8,

            "computer architecture": 0.6
        }
    },

    "Electronics / Hardware Engineer": {

        "icon": "⚡",

        "description":
            "Works with electronic circuits, hardware design, "
            "testing, sensors, and embedded systems.",

        "skills": {

            "electronics": 1.0,
            "analog electronics": 0.8,
            "digital electronics": 1.0,

            "circuit design": 1.0,

            "microcontroller": 0.8,

            "arduino": 0.7,
            "embedded systems": 0.8,

            "pcb": 1.0,
            "pcb design": 1.0,

            "altium": 0.8,
            "kicad": 0.8,

            "sensors": 0.7,

            "testing": 0.6,
            "debugging": 0.7
        }
    },

    "PLM / CAD Engineer": {

        "icon": "🧩",

        "description":
            "Works with product lifecycle management, CAD data, "
            "product structures, engineering data, and PLM systems.",

        "skills": {

            "plm": 1.0,
            "teamcenter": 1.0,

            "product lifecycle management": 1.0,
            "product data management": 0.9,

            "bmide": 0.9,

            "bom": 0.8,
            "workflow": 0.8,

            "cad": 0.9,
            "solidworks": 0.9,
            "autocad": 0.8,

            "catia": 0.8,
            "nx": 0.8,

            "access control": 0.6,

            "sql": 0.5,
            "java": 0.5
        }
    },

    "Business Analyst": {

        "icon": "📋",

        "description":
            "Analyzes business requirements, processes, data, "
            "and communicates solutions to stakeholders.",

        "skills": {

            "business analysis": 1.0,
            "requirements analysis": 1.0,

            "sql": 0.7,
            "excel": 0.9,

            "power bi": 0.8,
            "tableau": 0.7,

            "data analysis": 0.9,

            "communication": 0.8,
            "presentation": 0.7,

            "problem solving": 0.8,

            "agile": 0.7,
            "scrum": 0.6,

            "jira": 0.6,

            "documentation": 0.7
        }
    }
}

SKILL_ALIASES = {

    "python programming": "python",
    "python programming language": "python",
    "python development": "python",

    "java programming": "java",
    "java development": "java",

    "c programming": "c",
    "c language": "c",

    "c++ programming": "c++",

    "sql database": "sql",
    "mysql": "sql",
    "postgresql": "sql",
    "postgres": "sql",

    "html5": "html",
    "css3": "css",

    "javascript programming": "javascript",
    "js": "javascript",

    "reactjs": "react",
    "react.js": "react",

    "nodejs": "node.js",
    "node js": "node.js",

    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "rest api development": "rest api",

    "git version control": "git",
    "github version control": "github",

    "data analytics": "data analysis",
    "data analyst": "data analysis",

    "powerbi": "power bi",
    "power-bi": "power bi",

    "artificial intelligence": "ai",
    "gen ai": "generative ai",
    "genai": "generative ai",

    "large language models": "llm",
    "large language model": "llm",

    "embedded system": "embedded systems",
    "embedded software": "embedded systems",

    "microcontrollers": "microcontroller",
    "microcontroller programming": "microcontroller",

    "esp 8266": "esp8266",
    "esp-8266": "esp8266",

    "esp 32": "esp32",
    "esp-32": "esp32",

    "internet of things": "iot",

    "message queuing telemetry transport": "mqtt",

    "long range wide area network": "lorawan",

    "very large scale integration": "vlsi",

    "hardware description language": "verilog",

    "rtl design": "rtl",
    "rtl designing": "rtl",

    "teamcenter plm": "teamcenter",
    "siemens teamcenter": "teamcenter",

    "product lifecycle management": "plm",

    "computer aided design": "cad",

    "solid works": "solidworks",

    "software testing": "testing",
    "test automation": "automation",

    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "continuous integration and deployment": "ci/cd",

    "cyber security": "cybersecurity",
    "information security": "cybersecurity",

    "business requirements": "requirements analysis",
    "requirement analysis": "requirements analysis"
}

def _normalize_skill(skill):

    text = " ".join(
        str(skill)
        .lower()
        .strip()
        .split()
    )

    return SKILL_ALIASES.get(
        text,
        text
    )

def _skill_matches(
    resume_skill,
    required_skill
):

    resume_skill = _normalize_skill(
        resume_skill
    )

    required_skill = _normalize_skill(
        required_skill
    )

    if resume_skill == required_skill:
        return True

    if re.search(
        rf"(?<!\\w){re.escape(required_skill)}(?!\\w)",
        resume_skill
    ):
        return True

    if re.search(
        rf"(?<!\\w){re.escape(resume_skill)}(?!\\w)",
        required_skill
    ):
        return True

    return False

def calculate_role_fit(
    resume_skills,
    role_data
):

    cleaned_resume_skills = [

        _normalize_skill(skill)

        for skill in resume_skills

        if str(skill).strip()
    ]

    total_weight = sum(
        role_data["skills"].values()
    )

    matched = []
    missing = []

    for (
        required_skill,
        weight
    ) in role_data["skills"].items():

        found = any(

            _skill_matches(
                resume_skill,
                required_skill
            )

            for resume_skill
            in cleaned_resume_skills
        )

        if found:

            matched.append(
                required_skill
            )

        else:

            missing.append(
                (
                    required_skill,
                    weight
                )
            )

    matched_weight = sum(

        role_data["skills"][skill]

        for skill in matched
    )

    if total_weight > 0:

        score = round(
            (
                matched_weight
                / total_weight
            ) * 100
        )

    else:

        score = 0

    missing.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return {

        "score":
            min(
                100,
                max(
                    0,
                    score
                )
            ),

        "matched":
            matched,

        "missing":
            [
                skill
                for skill, weight
                in missing
            ]
    }

MIN_ROLE_MATCH_SCORE = 40

def simulate_roles(
    resume_skills
):

    results = []

    for (
        role_name,
        role_data
    ) in ROLE_DEFINITIONS.items():

        fit = calculate_role_fit(
            resume_skills,
            role_data
        )

        results.append({

            "role":
                role_name,

            "icon":
                role_data["icon"],

            "description":
                role_data["description"],

            **fit
        })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )

def get_qualified_role_matches(
    role_results,
    minimum_score=MIN_ROLE_MATCH_SCORE
):
    """
    Return only meaningful career-role matches.

    A role qualifies when:
    1. Its score is at least the minimum threshold.
    2. It has at least one matched skill.

    This prevents unrelated roles with scores such as
    8, 7, and 6 from being displayed as "Top Matches".
    """

    qualified_roles = []

    for role in role_results:

        score = role.get(
            "score",
            0
        )

        matched_skills = role.get(
            "matched",
            []
        )

        if (
            score >= minimum_score
            and isinstance(
                matched_skills,
                list
            )
            and len(matched_skills) > 0
        ):

            qualified_roles.append(
                role
            )

    return qualified_roles
