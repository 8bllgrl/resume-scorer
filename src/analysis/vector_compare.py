# src/analysis/vector_compare.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume_text, job_desc_text):
    """Returns a percentage match score using TF-IDF."""
    documents = [resume_text, job_desc_text]

    # We use sublinear_tf to prevent long resumes from 'cheating'
    # by repeating keywords.
    vectorizer = TfidfVectorizer(stop_words='english', sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compare the first doc (resume) with the second doc (job)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(score[0][0] * 100, 2)