# src/analysis/vector_compare.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume_text, job_desc_text):
    """Overall document comparison."""
    documents = [resume_text, job_desc_text]
    vectorizer = TfidfVectorizer(stop_words='english', sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(score[0][0] * 100, 2)


def score_line_against_text(line, reference_text):
    """
    Ranks a single resume line against the Job Description.
    This ensures we find the best 'answers' to the job requirements.
    """
    if not line.strip(): return 0.0

    # We fit the vectorizer on the Job Description (the 'source of truth')
    # and then transform the single line to see how it fits.
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([reference_text])
        line_vector = vectorizer.transform([line])
        score = cosine_similarity(line_vector, tfidf_matrix)
        return score[0][0] * 100
    except:
        return 0.0