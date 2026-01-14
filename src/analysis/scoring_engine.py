import json
import re
from pathlib import Path
from src.analysis.vector_compare import calculate_match_score
from src.utils.file_utils import get_bullet_points

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_json_config(filename):
    path = PROJECT_ROOT / "config" / filename
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def normalize_text(text, synonyms):
    """Aligns terminology (e.g., 'Amazon Web Services' -> 'aws') to boost scores."""
    text = text.lower()
    for standard, variations in synonyms.items():
        for var in variations:
            text = re.sub(rf'\b{re.escape(var.lower())}\b', standard.lower(), text)
    return text


def analyze_match(resume_path, job_path):
    # 1. Load Data
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_raw = f.read()
    with open(job_path, 'r', encoding='utf-8') as f:
        job_raw = f.read()

    inventory = load_json_config("skills_inventory.json")
    synonyms = load_json_config("synonyms.json")

    # 2. Pre-process
    norm_resume = normalize_text(resume_raw, synonyms)
    norm_job = normalize_text(job_raw, synonyms)

    # 3. Overall Match Score
    overall_score = calculate_match_score(norm_resume, norm_job)

    # 4. Keyword Detection
    found = []
    missing = []
    all_skills = [s for sublist in inventory.values() for s in sublist]

    for skill in all_skills:
        pattern = rf'\b{re.escape(skill.lower())}\b'
        if re.search(pattern, norm_job):
            if re.search(pattern, norm_resume):
                found.append(skill)
            else:
                missing.append(skill)

    # 5. Outdated Tech Flags
    outdated_list = ["flash", "angularjs", "silverlight", "vb6", "jquery"]
    red_flags = [t for t in outdated_list if t in norm_resume]

    # 6. Bullet Analysis (Top 5 / Worst 5)
    bullets = get_bullet_points(resume_raw)
    scored_bullets = []
    for b in bullets:
        # Score individual bullet vs the job
        b_score = calculate_match_score(normalize_text(b, synonyms), norm_job)
        scored_bullets.append((b.strip(), b_score))

    # Sort: Highest score first
    sorted_bullets = sorted(scored_bullets, key=lambda x: x[1], reverse=True)

    # Filter out very short lines (like contact info) for the 'Worst' list
    content_bullets = [b for b in sorted_bullets if len(b[0]) > 25]

    return {
        "score": overall_score,
        "found": sorted(list(set(found))),
        "missing": sorted(list(set(missing))),
        "red_flags": red_flags,
        "top_5": sorted_bullets[:5],
        "worst_5": content_bullets[-5:] if len(content_bullets) >= 10 else []
    }