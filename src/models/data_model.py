import re
import ssl
from collections import Counter

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.util import ngrams
from textblob import TextBlob

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download stopwords if they're not already downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def load_and_process_data(filepath='winter-lung.csv'):
    """
    Loads and processes the CSV data, converting date strings to datetime
    and handling numeric columns appropriately.
    """
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    numeric_columns = ['replies', 'reposts', 'likes', 'views', 'followers']

    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(',', '')

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


def get_sentiment(text):
    """Calculate sentiment using TextBlob"""
    try:
        return TextBlob(str(text)).sentiment.polarity
    except:
        return 0


def categorize_sentiment(polarity):
    """Categorize sentiment score"""
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    return 'Neutral'


def analyze_text_content(text, include_common=False):
    """
    Analyze text content using standard NLP techniques to extract meaningful phrases.
    Returns a list of tuples (phrase, count, frequency_score, num_words).
    """
    # Convert to string and lowercase
    text = str(text).lower()

    # Remove URLs and clean text
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Tokenize and clean
    tokens = [token.strip() for token in text.split() if len(token.strip()) > 2]

    # Get standard stopwords
    stop_words = set(stopwords.words('english'))
    if not include_common:
        stop_words.update(['rt', 'via', 'amp'])  # Minimal social media terms

    # Filter tokens
    filtered_tokens = [token for token in tokens if token not in stop_words]

    # Generate n-grams and their frequencies
    all_phrases = []
    total_tokens = len(filtered_tokens)

    for n in range(2, 9):
        n_grams = list(ngrams(filtered_tokens, n))
        phrase_counts = Counter(' '.join(gram) for gram in n_grams)

        for phrase, count in phrase_counts.items():
            words = phrase.split()
            num_words = len(words)

            # Calculate frequency score (TF - Term Frequency)
            frequency_score = count / total_tokens if total_tokens > 0 else 0

            all_phrases.append((phrase, count, frequency_score, num_words))

    # Sort by count (frequency) first, then by frequency_score
    return sorted(all_phrases, key=lambda x: (-x[1], -x[2]))


def get_word_frequency(text, include_common=False, min_words=2, max_words=5):
    """
    Get word frequencies filtered by word count and minimum frequency threshold.
    Returns a Counter object with significant phrases.
    """
    # Ensure text is a string and clean it
    text = str(text).lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)

    # Remove special characters but keep apostrophes for contractions
    text = re.sub(r'[^\w\s\']', ' ', text)

    # Remove numbers and extra whitespace
    text = re.sub(r'\d+', '', text)
    text = ' '.join(text.split())

    if not text.strip():
        return Counter()

    # Get stopwords
    stop_words = set(stopwords.words('english'))
    if not include_common:
        stop_words.update(['rt', 'via', 'amp', 'new', 'update'])

    # Tokenize and clean
    tokens = []
    for token in text.split():
        token = token.strip("'")  # Remove leading/trailing apostrophes
        if (len(token) > 2 and
                token not in stop_words and
                not token.startswith(("'", "#", "@"))):
            tokens.append(token)

    # Generate n-grams within word range
    phrases = []
    for n in range(min_words, max_words + 1):
        if n <= len(tokens):
            n_grams = ngrams(tokens, n)
            phrases.extend(' '.join(gram) for gram in n_grams)

    # Count frequencies and filter
    phrase_counts = Counter(phrases)
    min_freq = 2

    # Sort by frequency and return top phrases
    return Counter(dict(sorted(
        {phrase: count for phrase, count in phrase_counts.items()
         if count >= min_freq}.items(),
        key=lambda x: (-x[1], x[0])
    )))


def get_hashtag_frequency(texts):
    """Extract and count hashtags from texts"""
    hashtag_pattern = r'#(\w+)'
    hashtags = []

    for text in texts:
        if isinstance(text, str):
            hashtags.extend(re.findall(hashtag_pattern, text.lower()))

    return Counter(hashtags)


def get_location_counts(df):
    """Count posts by location"""
    locations = df['location'].fillna('Unknown')
    return locations.value_counts()