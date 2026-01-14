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

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from src.ui.components.job_popup import JobPopup
from src.analysis.scoring_engine import analyze_match
from src.utils.file_utils import extract_text_from_pdf, clean_resume_text


class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ResuBuilder v2.1")
        self.root.geometry("750x700")

        self.analyze_all_var = tk.BooleanVar(value=False)
        self.job_files = []
        self.resume_files = []

        tk.Label(root, text="Step 1: Import Materials", font=('Arial', 11, 'bold')).pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="📥 Import Resume", width=20, command=self.ui_import).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="📋 Paste New Job", width=20, command=self.ui_paste).pack(side=tk.LEFT, padx=10)

        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=30, pady=20)

        tk.Label(root, text="Step 2: Select Files to Compare", font=('Arial', 11, 'bold')).pack(pady=5)

        selection_frame = tk.Frame(root)
        selection_frame.pack(fill='both', expand=True, padx=20)

        # RESUME COLUMN
        res_frame = tk.Frame(selection_frame)
        res_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
        tk.Label(res_frame, text="Select Resume", font=('Arial', 9, 'italic')).pack()
        self.res_listbox = tk.Listbox(res_frame, height=10, exportselection=False)
        self.res_listbox.pack(fill='both', expand=True)

        # JOB COLUMN
        job_frame = tk.Frame(selection_frame)
        job_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
        tk.Label(job_frame, text="Select Job", font=('Arial', 9, 'italic')).pack()
        self.job_listbox = tk.Listbox(job_frame, height=10, exportselection=False)
        self.job_listbox.pack(fill='both', expand=True)

        self.refresh_lists()

        tk.Checkbutton(root, text="Analyze ALL cached resumes against selected job",
                       variable=self.analyze_all_var, command=self.toggle_res_list).pack(pady=10)

        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=30, pady=10)

        tk.Button(root, text="🚀 RUN MATCH ANALYSIS", width=40, bg="#2e7d32", fg="white",
                  font=('Arial', 12, 'bold'), command=self.ui_run).pack(pady=20)


    def toggle_res_list(self):
        """Disables the resume listbox if 'Analyze All' is checked."""
        if self.analyze_all_var.get():
            self.res_listbox.config(state=tk.DISABLED, bg="#f0f0f0")
        else:
            self.res_listbox.config(state=tk.NORMAL, bg="white")

    def refresh_lists(self):
        """Updates both listboxes with latest files."""
        # Refresh Resumes
        self.res_listbox.delete(0, tk.END)
        res_dir = PROJECT_ROOT / "data/cache/parsed_resumes"
        res_dir.mkdir(parents=True, exist_ok=True)
        self.resume_files = sorted(list(res_dir.glob("*.txt")), key=os.path.getmtime, reverse=True)
        for f in self.resume_files:
            self.res_listbox.insert(tk.END, f" 📄 {f.name}")

        # Refresh Jobs
        self.job_listbox.delete(0, tk.END)
        job_dir = PROJECT_ROOT / "data/job_descriptions"
        job_dir.mkdir(parents=True, exist_ok=True)
        self.job_files = sorted(list(job_dir.glob("*.txt")), key=os.path.getmtime, reverse=True)
        for f in self.job_files:
            self.job_listbox.insert(tk.END, f" 🎯 {f.name}")

    def ui_import(self):
        path = filedialog.askopenfilename(filetypes=[("Docs", "*.pdf *.txt")])
        if path:
            text = extract_text_from_pdf(path) if path.endswith('.pdf') else open(path, encoding='utf-8').read()
            clean = clean_resume_text(text)
            save_path = PROJECT_ROOT / "data/cache/parsed_resumes" / f"{Path(path).stem}.txt"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(clean)
            self.refresh_lists()
            messagebox.showinfo("Success", f"Resume '{Path(path).stem}' imported!")

    def ui_paste(self):
        JobPopup(self.root, on_confirm=self.ui_save_job)

    def ui_save_job(self, content):
        ts = datetime.now().strftime('%H%M%S')
        clean_name = re.sub(r'\W+', '', content.split('\n')[0][:10])
        path = PROJECT_ROOT / "data" / "job_descriptions" / f"{clean_name}_{ts}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.refresh_lists()

    def ui_run(self):
        # 1. Validate Job Selection
        job_selection = self.job_listbox.curselection()
        if not job_selection:
            messagebox.showwarning("Selection Required", "Please select a JOB from the right list.")
            return
        target_job = self.job_files[job_selection[0]]

        # 2. Determine Resume(s)
        if self.analyze_all_var.get():
            resumes_to_run = self.resume_files
        else:
            res_selection = self.res_listbox.curselection()
            if not res_selection:
                messagebox.showwarning("Selection Required", "Please select a RESUME or check 'Analyze ALL'.")
                return
            resumes_to_run = [self.resume_files[res_selection[0]]]

        if not resumes_to_run:
            messagebox.showerror("Error", "No resumes found.")
            return

        # 3. Execute
        print("\n" + "=" * 75 + f"\n🎯 MATCHING AGAINST JOB: {target_job.name}\n" + "=" * 75)
        for res in resumes_to_run:
            data = analyze_match(res, target_job)
            self.print_results(res.name, data)

    def print_results(self, name, data):
        print(f"\n📄 RESUME: {name}")
        print(f"📈 MATCH SCORE: {data['score']}%")
        print(f"✅ FOUND: {', '.join(data['found'])}")
        print(f"❌ MISSING: {', '.join(data['missing'][:5])}")

        if data.get('warnings'):
            print(f"⚠️ NEGATION DETECTED: {', '.join(data['warnings'])}")

        print("\nTOP MATCHING BULLETS:")
        for i, (txt, score) in enumerate(data['top_bullets'][:10], 1):
            print(f"  {i:2}. [{score:>5.2f}%] {txt[:110]}...")
        print("-" * 75)


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeApp(root)
    root.mainloop()