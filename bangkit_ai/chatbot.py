import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import vertexai
from vertexai.generative_models import GenerativeModel

# Inisialisasi Vertex AI
PROJECT_ID = "stunby-bangkit"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

class StunbyRAG:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.contexts = []
        self.answers = []
        self.context_vectors = None
    
    def fit(self, contexts, answers):
        self.contexts = contexts
        self.answers = answers
        self.context_vectors = self.vectorizer.fit_transform(contexts)
    
    def get_relevant_context(self, query, k=3):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.context_vectors)[0]
        top_k_idx = np.argsort(similarities)[-k:][::-1]
        return [self.contexts[i] for i in top_k_idx], [self.answers[i] for i in top_k_idx]

def load_model(path='models/generative'):
    from chatbot import StunbyRAG
    with open(f'{path}/stunby_rag.pkl', 'rb') as f:
        return pickle.load(f)

def stunby_chatbot(query, rag_model):
    # Retrieval
    relevant_contexts, relevant_answers = rag_model.get_relevant_context(query)
    combined_context = " ".join(relevant_contexts)

    # Generation dengan Gemini
    model = GenerativeModel("gemini-1.5-pro-002")
    prompt = f"""
    Berdasarkan konteks berikut:
    {combined_context}

    Jawablah pertanyaan ini:
    {query}

    Berikan jawaban yang ringkas dan relevan.
    """

    generation_config = {
        "temperature": 0.7,
        "max_output_tokens": 1024,
        "top_p": 0.9,
        "top_k": 40
    }

    response = model.generate_content(prompt, generation_config=generation_config)
    return response.text
