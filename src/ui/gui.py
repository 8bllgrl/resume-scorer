import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# --- PATH LOGIC ---
# This finds the "ResuBuilder" root directory regardless of where you run the script
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import your custom utility functions
try:
    from src.utils.file_utils import extract_text_from_pdf, clean_resume_text
except ImportError:
    messagebox.showerror("Error", "Could not find src/utils/file_utils.py. Please ensure it exists.")


class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Matcher Helper")
        self.root.geometry("400x250")

        # Ensure directory structure exists at root
        self.setup_directories()

        # --- UI LAYOUT ---
        tk.Label(root, text="Resume Assistant", font=('Arial', 12, 'bold')).pack(pady=10)

        tk.Button(root, text="1. Import New Resume (PDF/TXT)", width=30, command=self.import_resume).pack(pady=5)
        tk.Button(root, text="2. Paste Job Description", width=30, command=self.paste_job).pack(pady=5)

        tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=20, pady=10)

        tk.Button(root, text="3. RUN MATCH ANALYSIS", width=30, bg="green", fg="white", font=('Arial', 10, 'bold'),
                  command=self.run_analysis).pack(pady=5)

    def setup_directories(self):
        """Creates the necessary data folders at the project root."""
        paths = [
            PROJECT_ROOT / "data" / "resumes",
            PROJECT_ROOT / "data" / "job_descriptions",
            PROJECT_ROOT / "data" / "cache" / "parsed_resumes",
        ]
        for p in paths:
            p.mkdir(parents=True, exist_ok=True)

    def import_resume(self):
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("Resume Files", "*.pdf *.txt *.md")]
        )

        if not file_path:
            return

        print(f"\n[DEBUG] Processing Resume: {file_path}")

        # 1. Extraction
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            raw_text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()

        # 2. Cleaning
        cleaned_text = clean_resume_text(raw_text)

        # 3. Saving to Cache
        filename = Path(file_path).stem
        save_path = PROJECT_ROOT / "data" / "cache" / "parsed_resumes" / f"{filename}.txt"

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"[SUCCESS] Parsed text saved to: {save_path}")
        print(f"[DEBUG] Character count: {len(cleaned_text)}")

    def paste_job(self):
        self.job_popup = tk.Toplevel(self.root)
        self.job_popup.title("Paste Job Description")
        self.job_popup.attributes('-topmost', True)

        tk.Label(self.job_popup, text="Paste job text below and click Confirm:").pack(pady=5)

        self.job_text_area = scrolledtext.ScrolledText(self.job_popup, width=60, height=20)
        self.job_text_area.pack(padx=10, pady=10)

        # Enable Ctrl+V paste
        self.job_text_area.bind("<Control-v>", lambda e: self.job_text_area.event_generate("<<Paste>>"))

        tk.Button(self.job_popup, text="Confirm & Save", bg="blue", fg="white", command=self.save_job_description).pack(
            pady=5)

    def save_job_description(self):
        content = self.job_text_area.get("1.0", tk.END).strip()
        if not content:
            return

        # Generate clean filename from first line
        first_line = content.split('\n')[0][:20]
        clean_name = re.sub(r'\W+', '', first_line)
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{clean_name}_{timestamp}.txt"

        save_path = PROJECT_ROOT / "data" / "job_descriptions" / filename

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n--- JOB DESCRIPTION SAVED ---")
        print(f"Location: {save_path}")
        self.job_popup.destroy()

    def run_analysis(self):
        """Logic for comparing resumes to jobs."""
        print("\n" + "=" * 60)
        print("🔍 ANALYSIS ENGINE STARTING")
        print("=" * 60)

        # Check if we have files to compare
        job_dir = PROJECT_ROOT / "data" / "job_descriptions"
        cache_dir = PROJECT_ROOT / "data" / "cache" / "parsed_resumes"

        jobs = list(job_dir.glob("*.txt"))
        resumes = list(cache_dir.glob("*.txt"))

        if not jobs or not resumes:
            print("[ERROR] Missing files! Ensure you have imported a resume and saved a job.")
            return

        print(f"Found {len(resumes)} parsed resume(s) and {len(jobs)} job description(s).")
        print("\n[STUB] Next step: Implement TF-IDF scoring between these files...")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeApp(root)
    root.mainloop()