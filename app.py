import os
import nltk
import random
import string
import fitz  # PyMuPDF for PDF extraction
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure NLTK data is available
nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables to store chatbot knowledge
document_text = ""
sentence_tokens = []
word_tokens = []
lemmer = nltk.stem.WordNetLemmatizer()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()

# Tokenization, Lemmatization
def lem_tokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def lem_normalize(text):
    return lem_tokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

# Greeting function
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey")
GREETING_RESPONSES = ["hi", "hey", "hello", "hi there", "I am glad! You are talking to me"]

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

# Generate response
def generate_response(user_query):
    global sentence_tokens

    sentence_tokens.append(user_query)
    TfidVec = TfidfVectorizer(tokenizer=lem_normalize, stop_words='english')
    tfidf = TfidVec.fit_transform(sentence_tokens)

    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    best_response_score = flat[-2]

    if best_response_score == 0:
        return "I'm sorry! I don't understand your question."
    else:
        return sentence_tokens[idx]

# Upload PDF Route
@app.route('/upload', methods=['POST'])
def upload_pdf():
    global document_text, sentence_tokens, word_tokens

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        document_text = extract_text_from_pdf(pdf_path)
        sentence_tokens = nltk.sent_tokenize(document_text)
        word_tokens = nltk.word_tokenize(document_text)

        return jsonify({"message": "PDF uploaded and processed successfully!"})
    else:
        return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400

# Chatbot API
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    if user_message.lower() == "bye":
        return jsonify({"response": "Bye! Take care."})

    if greeting(user_message) is not None:
        return jsonify({"response": greeting(user_message)})

    bot_response = generate_response(user_message)
    sentence_tokens.pop(-1)  # Remove user query to avoid duplication

    return jsonify({"response": bot_response})

# UI Route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
