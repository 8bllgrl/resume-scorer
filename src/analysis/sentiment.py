from textblob import TextBlob


def is_context_positive(text, keyword):
    """
    Checks if a keyword is used negatively (e.g., 'no experience with...')
    Returns True if safe, False if it's a 'lack of' statement.
    """
    # Find the sentence containing the keyword to analyze context
    sentences = text.lower().split('.')
    target_sentence = next((s for s in sentences if keyword.lower() in s), "")

    if not target_sentence:
        return True

    # Check for simple negation words within 3 words of the keyword
    negations = ["no", "none", "never", "lack", "without", "learning", "minimal", "want"]
    words = target_sentence.split()

    try:
        idx = words.index(keyword.lower())
        context_window = words[max(0, idx - 3): idx]
        if any(neg in context_window for neg in negations):
            return False
    except ValueError:
        pass

    # Fallback to TextBlob for general tone
    analysis = TextBlob(target_sentence)
    if analysis.sentiment.polarity < -0.2:
        return False

    return True