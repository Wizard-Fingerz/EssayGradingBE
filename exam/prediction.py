import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

warnings.simplefilter("ignore")

# class PredictionService:
#     def __init__(self):
#         self.model = self.load_model()
#         self.tfidf_vectorizer = self.load_tfidf_vectorizer()

#     def load_model(self):
#         model_path = './model/dt_model.joblib'
#         try:
#             model = joblib.load(model_path)
#             return model
#         except Exception as e:
#             print(f"Error loading the model: {e}")
#             return None

#     def load_tfidf_vectorizer(self):
#         vectorizer_path = './model/tfidf_vectorizer.joblib'
#         try:
#             vectorizer = joblib.load(vectorizer_path)
#             return vectorizer
#         except Exception as e:
#             print(f"Error loading the TF-IDF vectorizer: {e}")
#             return None

#     def preprocess_text(self, text):
#         # Tokenize the text into words
#         tokens = word_tokenize(text.lower())
#         # Remove stopwords
#         stop_words = set(stopwords.words('english'))
#         tokens = [word for word in tokens if word not in stop_words]
#         # Lemmatize the words
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(word) for word in tokens]
#         # Join the preprocessed tokens back into a single string
#         return ' '.join(tokens)

#     def predict(self, question_id, comprehension, question, examiner_answer, student_answer, question_score):
#         if self.model is None or self.tfidf_vectorizer is None:
#             print("Model or TF-IDF vectorizer is not initialized. Skipping prediction.")
#             return None

#         # Preprocess text data
#         preprocessed_comprehension = self.preprocess_text(comprehension)
#         preprocessed_question = self.preprocess_text(question)
#         preprocessed_examiner_answer = self.preprocess_text(examiner_answer)
#         preprocessed_student_answer = self.preprocess_text(student_answer)

#         # Combine preprocessed text into a single string
#         combined_text = f"{preprocessed_comprehension} {preprocessed_question} {preprocessed_examiner_answer} {preprocessed_student_answer}"

#         try:
#             # Vectorize input text using TF-IDF vectorizer
#             input_data_vectorized = self.tfidf_vectorizer.transform([combined_text])

#             # Combine numerical and text features
#             X_combined = pd.concat([pd.DataFrame(input_data_vectorized.toarray()), pd.DataFrame(question_score)], axis=1)

#             # Make prediction using the model
#             prediction = self.model.predict(X_combined)
#             return prediction[0]  # Assuming a single prediction is made
#         except Exception as e:
#             print(f"Error making prediction: {e}")
#             return None

#     def fit(self, X, y):
#         # Train the model
#         try:
#             self.model.fit(X, y)
#         except Exception as e:
#             print(f"Error fitting the model: {e}")

#     def save_model(self, model_path='./model/dt_model.joblib'):
#         # Save the trained model
#         try:
#             joblib.dump(self.model, model_path)
#             print("Model saved successfully.")
#         except Exception as e:
#             print(f"Error saving the model: {e}")


import joblib
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy's medium-sized English language model
nlp = spacy.load("en_core_web_md")

class PredictionService:
    def __init__(self):
        self.model = self.load_model()

    
    def load_model(self):
        model_path = './model/dt_model_new.joblib'
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            print(f"Error loading the model: {e}")
            return None


    def preprocess_text(self, text):
        # Convert text to lowercase
        text = text.lower()
        text = ''.join([char for char in text if char.isalnum() or char.isspace()])
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(tokens)

    def calculate_combined_similarity(self, student_answer, examiner_answer, comprehension, weights):
        # Check if any of the input text strings are empty
        if not student_answer or not examiner_answer or not comprehension:
            return 0.0  # Return zero similarity if any input text string is empty
        
        # Preprocess the text
        preprocessed_student_answer = self.preprocess_text(student_answer)
        preprocessed_examiner_answer = self.preprocess_text(examiner_answer)
        preprocessed_comprehension = self.preprocess_text(comprehension)
        
        # Calculate similarity between student answer and examiner answer
        similarity_examiner = nlp(preprocessed_student_answer).similarity(nlp(preprocessed_examiner_answer))
        
        # Calculate similarity between student answer and comprehension
        similarity_comprehension = nlp(preprocessed_student_answer).similarity(nlp(preprocessed_comprehension))
        
        # Combine similarity scores using weights
        combined_similarity = (weights['examiner'] * similarity_examiner) + (weights['comprehension'] * similarity_comprehension)
        
        return combined_similarity

    def predict(self, question_id, comprehension, question, examiner_answer, student_answer, question_score, suppress_warning=True):
        # Specify weights for examiner answer and comprehension
        weights = {'examiner': 0.7, 'comprehension': 0.3}
        
        # Calculate semantic similarity
        semantic_similarity = self.calculate_combined_similarity(student_answer, examiner_answer, comprehension, weights)
        
        # Assuming you have loaded your model and preprocessed the text
        
        # Make prediction using your machine learning model
        predicted_student_score = self.model.predict([semantic_similarity])
        
        # Ensure the predicted score does not exceed the question score
        predicted_student_score = min(predicted_student_score, question_score)
        
        return predicted_student_score