import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from rouge import Rouge
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Calculate evaluation scores.')
parser.add_argument('--output-dir', required=True, help='Directory containing output files')
parser.add_argument('--results-dir', required=True, help='Directory to store the evaluation results')
args = parser.parse_args()

# Load and parse data
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Vectorizer for text similarity
vectorizer = TfidfVectorizer()

# Evaluation metrics
def relevance_score(input_text, source_texts):
    """Calculates average cosine similarity between input text and source documents."""
    if not source_texts:
        return 0.0
    tfidf = vectorizer.fit_transform([input_text] + source_texts)
    cosine_similarities = cosine_similarity(tfidf[0:1], tfidf[1:])
    return cosine_similarities.mean()

def accuracy_metric(predicted, reference):
    """
    Calculates the ROUGE scores between the predicted response and reference response.
    `predicted` is the model-generated string.
    `reference` is a single reference string.
    
    Returns a dictionary containing ROUGE-1, ROUGE-2, and ROUGE-L scores.
    """
    rouge = Rouge()
    scores = rouge.get_scores(predicted, reference)
    return scores[0]

# Create results directory if it doesn't exist
os.makedirs(args.results_dir, exist_ok=True)

# Process each output file
for filename in os.listdir(args.output_dir):
    if filename.endswith('.json'):
        output_file = os.path.join(args.output_dir, filename)
        output_data = load_data(output_file)

        # Process the output data
        query = output_data['prompt']
        predicted_response = output_data['ai_answer']
        expected_response = output_data['expected_answer']

        # Sources list
        sources = [src['content'] for src in output_data['sources']] if output_data['sources'] else []

        # Calculate metrics
        relevance = relevance_score(predicted_response, sources)
        accuracy = accuracy_metric(predicted_response, expected_response)

        # Create result object
        result = {
            'query': query,
            'relevance_score': relevance,
            'accuracy': accuracy
        }

        # Save result to JSON file
        result_file = os.path.join(args.results_dir, f"{os.path.splitext(filename)[0]}_result.json")
        with open(result_file, 'w') as file:
            json.dump(result, file, indent=2)

print(f"Evaluation completed. Results stored in {args.results_dir}.")
