# ResuBuilder

A Python-based resume optimization tool that uses NLP (Natural Language Processing) to match resumes against job descriptions.

## ✨ Key Features
* **TF-IDF Scoring:** Uses vector similarity to give an objective match percentage.
* **Synonym Normalization:** Automatically recognizes that "AWS" is "Amazon Web Services".
* **Strategic Ranking:** Identifies your **Top 5** most relevant bullets and **Worst 5** "dead weight" bullets for tailoring.
* **Outdated Tech Detection:** Flags legacy tech like Flash or AngularJS that might hurt a modern application.

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **NLP:** Scikit-learn (TF-IDF), Regex
* **UI:** Tkinter
* **Data:** PyMuPDF (PDF Extraction)