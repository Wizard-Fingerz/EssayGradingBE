import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

warnings.simplefilter("ignore", category=InconsistentVersionWarning)

class PredictionService:
    def __init__(self):
        self.model = self.load_model()
        self.tfidf_vectorizer = joblib.load('./model/tfidf_vectorizer.joblib')  # Load the TF-IDF vectorizer
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()  # Get feature names

    def load_model(self):
        model_path = './model/dt_model.joblib'
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            print(f"Error loading the model: {e}")
            return None

    def preprocess_text(self, text):
        # Convert text to lowercase
        text = text.lower()
        # Remove non-alphanumeric characters and keep spaces
        text = ''.join([char for char in text if char.isalnum() or char.isspace()])
        # Tokenize the text into words
        tokens = word_tokenize(text)
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        # Lemmatize the words
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        # Join the preprocessed tokens back into a single string
        return ' '.join(tokens)

    def predict(self, question_id, comprehension, question, examiner_answer, student_answer, question_score, suppress_warning=True):
        if self.model is None:
            print("Model attribute is not initialized. Skipping prediction.")
            return None

        # Preprocess text data
        preprocessed_comprehension = self.preprocess_text(comprehension)
        preprocessed_question = self.preprocess_text(question)
        preprocessed_examiner_answer = self.preprocess_text(examiner_answer)
        preprocessed_student_answer = self.preprocess_text(student_answer)

        # Combine preprocessed text into a single string
        input_text = f"{question_id} {preprocessed_comprehension} {preprocessed_question} {preprocessed_examiner_answer} {question_score} {preprocessed_student_answer}"

        # Vectorize input text using TF-IDF vectorizer
        input_data_text = self.tfidf_vectorizer.transform([input_text])

        # Combine numerical and text features
        input_data_combined = pd.concat([pd.DataFrame([[question_score]]), pd.DataFrame(input_data_text.toarray())], axis=1)

        try:
            # Suppress warnings if specified
            if suppress_warning:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # Make prediction using the model
                    prediction = self.model.predict(input_data_combined)
            else:
                # Make prediction using the model without suppressing warnings
                prediction = self.model.predict(input_data_combined)
            
            return prediction[0]  # Assuming a single prediction is made
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
