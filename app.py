import json
import os
import nltk
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

app = Flask(__name__)

# Load FAQ data
FAQ_FILE = 'faq_data.json'
with open(FAQ_FILE, 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

questions = [item['question'] for item in faq_data]
answers = [item['answer'] for item in faq_data]

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize, stop_words='english', token_pattern=None)
X = vectorizer.fit_transform(questions)

def get_best_match(user_query, threshold=0.2):
    # Vectorize the user query
    user_query_vec = vectorizer.transform([user_query])
    
    # Calculate cosine similarity
    similarities = cosine_similarity(user_query_vec, X)
    
    # Get the index of the most similar question
    best_match_idx = similarities.argmax()
    best_match_score = similarities[0, best_match_idx]
    
    if best_match_score >= threshold:
        return answers[best_match_idx]
    else:
        return "I'm sorry, I don't have an answer to that question. Please try rephrasing or contact our human support team."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
        
    bot_response = get_best_match(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
