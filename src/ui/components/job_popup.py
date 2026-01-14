# src/ui/components/job_popup.py
import tkinter as tk
from tkinter import scrolledtext, messagebox


class JobPopup(tk.Toplevel):
    def __init__(self, master, on_confirm):
        super().__init__(master)
        self.title("Paste Job Description")
        self.attributes('-topmost', True)
        self.on_confirm = on_confirm

        tk.Label(self, text="Paste job text below and click Confirm:").pack(pady=10)
        self.text_area = scrolledtext.ScrolledText(self, width=70, height=25)
        self.text_area.pack(padx=15, pady=5)

        # Explicit Paste Binding
        self.text_area.bind("<Control-v>", lambda e: self.text_area.event_generate("<<Paste>>"))

        tk.Button(self, text="Confirm & Save", bg="#1565c0", fg="white",
                  command=self._confirm).pack(pady=10)

    def _confirm(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            self.on_confirm(content)
            self.destroy()
        else:
            messagebox.showwarning("Empty", "Please paste text first!")