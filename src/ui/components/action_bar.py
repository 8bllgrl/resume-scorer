# src/ui/components/action_bar.py
import tkinter as tk


class ActionBar(tk.Frame):
    def __init__(self, master, on_import, on_paste, on_run):
        super().__init__(master)

        tk.Label(self, text="Resume Assistant", font=('Arial', 14, 'bold')).pack(pady=15)

        tk.Button(self, text="1. Import New Resume", width=35, height=2,
                  command=on_import).pack(pady=5)

        tk.Button(self, text="2. Paste Job Description", width=35, height=2,
                  command=on_paste).pack(pady=5)

        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=30, pady=15)

        tk.Button(self, text="3. RUN MATCH ANALYSIS", width=35, height=2,
                  bg="#2e7d32", fg="white", font=('Arial', 10, 'bold'),
                  command=on_run).pack(pady=5)