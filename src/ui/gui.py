# # src/ui/gui.py
# import tkinter as tk
# from tkinter import filedialog, messagebox
# import sys
# import os
# from datetime import datetime
# from pathlib import Path
#
# PROJECT_ROOT = Path(__file__).parent.parent.parent
# sys.path.append(str(PROJECT_ROOT))
#
# from src.ui.components.job_popup import JobPopup
# from src.analysis.scoring_engine import analyze_match
# from src.utils.file_utils import extract_text_from_pdf, clean_resume_text
#
#
# class ResumeApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Resume Matcher Helper")
#         self.root.geometry("450x300")
#         self._setup_folders()
#
#         tk.Label(root, text="Resume Assistant", font=('Arial', 14, 'bold')).pack(pady=20)
#
#         tk.Button(root, text="1. Import Resume", width=30, command=self.import_file).pack(pady=5)
#         tk.Button(root, text="2. Paste Job", width=30, command=self.open_paste_popup).pack(pady=5)
#
#         tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=40, pady=20)
#
#         tk.Button(root, text="3. RUN MATCH ANALYSIS", width=30, bg="green", fg="white",
#                   command=self.run_engine).pack(pady=5)
#
#     def _setup_folders(self):
#         for folder in ["data/cache/parsed_resumes", "data/job_descriptions", "config"]:
#             (PROJECT_ROOT / folder).mkdir(parents=True, exist_ok=True)
#
#     def import_file(self):
#         path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.txt")])
#         if path:
#             text = extract_text_from_pdf(path) if path.endswith('.pdf') else open(path).read()
#             clean = clean_resume_text(text)
#             save_to = PROJECT_ROOT / "data" / "cache" / "parsed_resumes" / f"{Path(path).stem}.txt"
#             with open(save_to, "w", encoding="utf-8") as f:
#                 f.write(clean)
#             print(f"[INFO] Resume Cached: {save_to.name}")
#
#     def open_paste_popup(self):
#         JobPopup(self.root, on_confirm=self.save_job)
#
#     def save_job(self, content):
#         name = re.sub(r'\W+', '', content.split('\n')[0][:15])
#         ts = datetime.now().strftime('%H%M%S')
#         path = PROJECT_ROOT / "data" / "job_descriptions" / f"{name}_{ts}.txt"
#         with open(path, "w", encoding="utf-8") as f:
#             f.write(content)
#         print(f"[INFO] Job Saved: {path.name}")
#
#     def run_engine(self):
#         # Fix for Windows Console encoding (The "ðŸ" fix)
#         if sys.platform == "win32":
#             os.system('chcp 65001 > nul')
#
#         print("\n" + "=" * 60 + "\n--- ANALYSIS STARTING ---\n" + "=" * 60)
#
#         resumes = list((PROJECT_ROOT / "data/cache/parsed_resumes").glob("*.txt"))
#         jobs = sorted((PROJECT_ROOT / "data/job_descriptions").glob("*.txt"), key=os.path.getmtime, reverse=True)
#
#         if not resumes or not jobs:
#             print("[ERROR] Missing files.")
#             return
#
#         latest_job = jobs[0]
#         for res in resumes:
#             res_data = analyze_match(res, latest_job)
#             print(f"\nFILE: {res.name}")
#             print(f"MATCH: {res_data['score']}%")
#             print(f"SKILLS: {', '.join(res_data['found'])}")
#             print(f"MISSING: {', '.join(res_data['missing'][:5])}")
#             print("\nTOP BULLETS:")
#             for i, (txt, score) in enumerate(res_data['top_bullets'][:3], 1):
#                 print(f" {i}. [{score}%] {txt[:100]}...")
#         print("\n" + "=" * 60)
#
#
# import re  # Added for the name cleaning in save_job
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ResumeApp(root)
#     root.mainloop()