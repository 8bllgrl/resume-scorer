import sys
import os
from pathlib import Path

# --- DYNAMIC PATH SETUP ---
try:
    current_path = Path(__file__).resolve()
    # Find root by looking for 'src'
    PROJECT_ROOT = next(p for p in current_path.parents if (p / "src").exists())
except StopIteration:
    PROJECT_ROOT = Path(__file__).parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.utils.file_utils import get_bullet_points

def aggregate_all_bullets():
    """Collects every bullet from cached resumes into one master file."""
    cache_dir = PROJECT_ROOT / "data" / "cache" / "parsed_resumes"
    output_dir = PROJECT_ROOT / "data" / "exports"
    output_file = output_dir / "master_bullet_list.txt"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not cache_dir.exists():
        print(f"Error: Cache directory not found at {cache_dir}")
        return

    all_resumes = list(cache_dir.glob("*.txt"))
    if not all_resumes:
        print("No resumes found to aggregate.")
        return

    unique_bullets = set()
    print(f"Processing {len(all_resumes)} resumes...")

    for res_path in all_resumes:
        try:
            with open(res_path, 'r', encoding='utf-8') as f:
                content = f.read()
                bullets = get_bullet_points(content)
                for b in bullets:
                    clean_b = b.strip()
                    if clean_b:
                        unique_bullets.add(clean_b)
        except Exception as e:
            print(f"Skipping {res_path.name}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"=== MASTER BULLET LIST ===\n\n")
        # Sort for easier manual review
        for bullet in sorted(list(unique_bullets)):
            if not bullet.startswith(('•', '-', '*')):
                f.write(f"• {bullet}\n")
            else:
                f.write(f"{bullet}\n")

    print(f"Successfully created master list: {output_file}")

if __name__ == "__main__":
    aggregate_all_bullets()