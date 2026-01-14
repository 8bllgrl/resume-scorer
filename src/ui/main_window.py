import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ui.components.job_popup import JobPopup
from src.analysis.scoring_engine import analyze_match
from src.utils.file_utils import extract_text_from_pdf, clean_resume_text


class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ResuBuilder v2.0")
        self.root.geometry("450x300")

        # UI Elements
        tk.Label(root, text="Resume Matcher", font=('Arial', 14, 'bold')).pack(pady=20)
        tk.Button(root, text="1. Import Resume", width=30, command=self.ui_import).pack(pady=5)
        tk.Button(root, text="2. Paste Job", width=30, command=self.ui_paste).pack(pady=5)

        tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=40, pady=20)
        tk.Button(root, text="3. RUN ANALYSIS", width=30, bg="#2e7d32", fg="white",
                  command=self.ui_run).pack(pady=5)

    def ui_import(self):
        path = filedialog.askopenfilename(filetypes=[("Docs", "*.pdf *.txt")])
        if path:
            text = extract_text_from_pdf(path) if path.endswith('.pdf') else open(path).read()
            clean = clean_resume_text(text)
            save_path = PROJECT_ROOT / "data/cache/parsed_resumes" / f"{Path(path).stem}.txt"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(clean)
            messagebox.showinfo("Success", "Resume Cached!")

    def ui_paste(self):
        JobPopup(self.root, on_confirm=self.ui_save_job)

    def ui_save_job(self, content):
        from datetime import datetime
        ts = datetime.now().strftime('%H%M%S')
        path = PROJECT_ROOT / "data/job_descriptions" / f"job_{ts}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Job Saved: {path.name}")

    def ui_run(self):
        # Setup Windows encoding for emojis/symbols
        if sys.platform == "win32": os.system('chcp 65001 > nul')

        print("\n" + "=" * 70 + "\n🚀 STARTING ANALYSIS\n" + "=" * 70)

        res_dir = PROJECT_ROOT / "data/cache/parsed_resumes"
        job_dir = PROJECT_ROOT / "data/job_descriptions"

        resumes = list(res_dir.glob("*.txt"))
        jobs = sorted(job_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)

        if not resumes or not jobs:
            print("❌ Error: Missing files in data folders.")
            return

        latest_job = jobs[0]
        for res in resumes:
            data = analyze_match(res, latest_job)

            print(f"📄 FILE: {res.name}")
            print(f"📊 MATCH: {data['score']}%")
            print(f"✅ SKILLS: {', '.join(data['found'])}")
            print(f"❓ MISSING: {', '.join(data['missing'][:5])}")

            if data['red_flags']:
                print(f"⚠️  WARNING: Outdated tech found: {', '.join(data['red_flags'])}")

            print(f"\n🔥 TOP 5 BULLETS (Keep/Promote):")
            for i, (txt, score) in enumerate(data['top_5'], 1):
                print(f"   {i}. [{score}%] {txt[:85]}...")

            print(f"\n🧊 WORST 5 BULLETS (Rewrite/Remove):")
            for i, (txt, score) in enumerate(data['worst_5'], 1):
                print(f"   {i}. [{score}%] {txt[:85]}...")

            print("-" * 70)


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeApp(root)
    root.mainloop()