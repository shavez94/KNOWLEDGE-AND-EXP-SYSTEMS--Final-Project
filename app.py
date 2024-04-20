import csv
from flask import Flask, render_template, request
from Levenshtein import distance

app = Flask(__name__)

# Load the CSV files into dictionaries
tenant_dict = {}
landlord_dict = {}
with open('tenant.csv', newline='', encoding='utf-8') as tenant_csvfile:
    tenant_reader = csv.DictReader(tenant_csvfile)
    for row in tenant_reader:
        tenant_dict[row['instruction']] = row['output']

with open('landlord.csv', newline='', encoding='utf-8') as landlord_csvfile:
    landlord_reader = csv.DictReader(landlord_csvfile)
    for row in landlord_reader:
        landlord_dict[row['instruction']] = row['output']

def calculate_distance(user_input, questions):
    distances = []
    for question in questions:
        dist = distance(user_input.lower(), question.lower())
        distances.append((question, dist))
    return distances

def get_suggestions(user_input, questions, n=5):
    distances = calculate_distance(user_input, questions)
    distances.sort(key=lambda x: x[1])
    suggestions = [q[0] for q in distances[:n]]
    return suggestions

# Define the route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Define the route for the questions page
@app.route('/questions', methods=['POST'])
def questions():
    role = request.form['role']
    question = request.form['question']
    if role == 'tenant':
        tenant_questions = list(tenant_dict.keys())
        suggestions = get_suggestions(question, tenant_questions)
    elif role == 'landlord':
        landlord_questions = list(landlord_dict.keys())
        suggestions = get_suggestions(question, landlord_questions)
    else:
        suggestions = []
    answer = None
    if question in tenant_dict:
        answer = tenant_dict[question]
    elif question in landlord_dict:
        answer = landlord_dict[question]
    return render_template('questions.html', question=question, answer=answer, suggestions=suggestions)

def get_words(s):
    words = set(s.split())
    return words

def get_suggestions(user_input, questions, n=5):
    user_words = get_words(user_input)
    suggestions = []
    for question in questions:
        question_words = get_words(question)
        common_words = user_words.intersection(question_words)
        if len(common_words) / len(user_words) > 0.5:
            suggestions.append(question)
    suggestions = suggestions[:n]
    return suggestions

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)