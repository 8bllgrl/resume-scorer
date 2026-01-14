import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Setup project root and Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Fix for Windows console emoji support
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from src.ui.components.job_popup import JobPopup
from src.analysis.scoring_engine import analyze_match
from src.utils.file_utils import extract_text_from_pdf, clean_resume_text


class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ResuBuilder v2.1")
        self.root.geometry("500x650")

        self.analyze_all_var = tk.BooleanVar(value=False)
        self.job_files = []

        # --- UI LAYOUT ---
        tk.Label(root, text="Step 1: Prep Data", font=('Arial', 10, 'bold')).pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Import Resume", width=15, command=self.ui_import).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Paste New Job", width=15, command=self.ui_paste).pack(side=tk.LEFT, padx=5)

        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=15)

        tk.Label(root, text="Step 2: Select Job to Match Against", font=('Arial', 10, 'bold')).pack()
        self.job_listbox = tk.Listbox(root, height=6, width=50)
        self.job_listbox.pack(pady=5, padx=20)
        self.refresh_job_list()

        tk.Checkbutton(root, text="Analyze ALL cached resumes", variable=self.analyze_all_var).pack(pady=5)
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=15)

        tk.Button(root, text="3. RUN ANALYSIS", width=35, bg="#2e7d32", fg="white",
                  font=('Arial', 11, 'bold'), command=self.ui_run).pack(pady=10)

    def refresh_job_list(self):
        self.job_listbox.delete(0, tk.END)
        job_dir = PROJECT_ROOT / "data" / "job_descriptions"
        job_dir.mkdir(parents=True, exist_ok=True)
        self.job_files = sorted(list(job_dir.glob("*.txt")), key=os.path.getmtime, reverse=True)
        for file in self.job_files:
            self.job_listbox.insert(tk.END, f" 📄 {file.name}")

    def ui_import(self):
        path = filedialog.askopenfilename(filetypes=[("Docs", "*.pdf *.txt")])
        if path:
            text = extract_text_from_pdf(path) if path.endswith('.pdf') else open(path, encoding='utf-8').read()
            clean = clean_resume_text(text)
            save_path = PROJECT_ROOT / "data" / "cache" / "parsed_resumes" / f"{Path(path).stem}.txt"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(clean)
            messagebox.showinfo("Success", f"Resume '{Path(path).stem}' ready!")

    def ui_paste(self):
        JobPopup(self.root, on_confirm=self.ui_save_job)

    def ui_save_job(self, content):
        ts = datetime.now().strftime('%H%M%S')
        clean_name = re.sub(r'\W+', '', content.split('\n')[0][:10])
        path = PROJECT_ROOT / "data" / "job_descriptions" / f"{clean_name}_{ts}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.refresh_job_list()

    def ui_run(self):
        selection = self.job_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please click on a job in the list first.")
            return

        target_job = self.job_files[selection[0]]
        res_dir = PROJECT_ROOT / "data" / "cache" / "parsed_resumes"
        resumes = list(res_dir.glob("*.txt"))

        if not resumes:
            messagebox.showerror("Error", "No cached resumes found.")
            return

        if not self.analyze_all_var.get():
            resumes = [max(resumes, key=os.path.getmtime)]

        print("\n" + "=" * 75 + f"\n🎯 MATCHING AGAINST: {target_job.name}\n" + "=" * 75)
        for res in resumes:
            data = analyze_match(res, target_job)
            self.print_results(res.name, data)

    def print_results(self, name, data):
        print(f"\n📄 RESUME: {name}")
        print(f"📈 MATCH SCORE: {data['score']}%")
        print(f"✅ FOUND: {', '.join(data['found'])}")
        print(f"❌ MISSING: {', '.join(data['missing'][:5])}")

        if data.get('warnings'):
            print(f"⚠️ NEGATION DETECTED (Skills you mentioned not having): {', '.join(data['warnings'])}")

        if data.get('red_flags'):
            print(f"🚩 RED FLAGS: {', '.join(data['red_flags'])}")

        print("\nTOP 10 BEST MATCHING BULLETS:")
        for i, (txt, score) in enumerate(data['top_bullets'], 1):
            print(f"  {i:2}. [{score:>5.2f}%] {txt[:120]}...")
        print("-" * 75)


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeApp(root)
    root.mainloop()