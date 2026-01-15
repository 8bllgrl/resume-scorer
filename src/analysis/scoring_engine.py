import json
import re
from pathlib import Path
from src.analysis.vector_compare import calculate_match_score, score_line_against_text
from src.utils.file_utils import get_bullet_points, structural_split
from src.analysis.sentiment import is_context_positive

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_json_config(filename):
    """Utility to load configuration files."""
    path = PROJECT_ROOT / "config" / filename
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def normalize_text(text, synonyms):
    """Aligns terminology based on the synonyms.json config."""
    if not text: return ""
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

    # NEW: Pre-process structural markers
    resume_raw = structural_split(resume_raw)
    job_raw = structural_split(job_raw)

    inventory = load_json_config("skills_inventory.json")
    synonyms = load_json_config("synonyms.json")
    filters = load_json_config("filters.json")
    settings = load_json_config("settings.json")

    # Load specific settings with safe fallbacks
    top_k = settings.get("top_k_count", 10)
    do_dedupe = settings.get("deduplicate_bullets", True)
    min_len = settings.get("min_bullet_length", 25)
    ignore_patterns = filters.get("ignore_patterns", [])

    # 2. Pre-process (Directly calling the function above)
    norm_resume = normalize_text(resume_raw, synonyms)
    norm_job = normalize_text(job_raw, synonyms)

    # 3. Overall Match Score
    overall_score = calculate_match_score(norm_resume, norm_job)

    # 4. Keyword Detection with Sentiment Context
    found, missing, warnings = [], [], []
    all_skills = [s for sublist in inventory.values() for s in sublist]

    for skill in all_skills:
        pattern = rf'\b{re.escape(skill.lower())}\b'
        if re.search(pattern, norm_job):
            if re.search(pattern, norm_resume):
                if is_context_positive(norm_resume, skill):
                    found.append(skill)
                else:
                    warnings.append(skill)
            else:
                missing.append(skill)

    # 5. Outdated Tech Penalty Flags
    outdated_list = ["flash", "angularjs", "silverlight", "vb6", "jquery"]
    red_flags = [t for t in outdated_list if t in norm_resume.lower()]

    # 6. Bullet Point Ranking with Deduplication
    bullets = get_bullet_points(resume_raw)
    scored_bullets = []
    seen_content = set()

    for b in bullets:
        clean_b = b.strip()

        # Filter: Length & Ignore Patterns
        if len(clean_b) < min_len: continue
        if any(re.search(p, clean_b, re.IGNORECASE) for p in ignore_patterns): continue

        # Deduplication check
        content_key = re.sub(r'\W+', '', clean_b).lower()
        if do_dedupe and content_key in seen_content:
            continue
        seen_content.add(content_key)

        # Scoring: Rank YOUR resume lines by how well they answer the JOB
        b_score = score_line_against_text(normalize_text(clean_b, synonyms), norm_job)
        scored_bullets.append((clean_b, b_score))

    # Sort and slice based on config
    sorted_bullets = sorted(scored_bullets, key=lambda x: x[1], reverse=True)

    return {
        "score": overall_score,
        "found": sorted(list(set(found))),
        "missing": sorted(list(set(missing))),
        "warnings": sorted(list(set(warnings))),
        "red_flags": red_flags,
        "top_bullets": sorted_bullets[:top_k]
    }