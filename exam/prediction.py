import joblib
import numpy as np
from sklearn.exceptions import InconsistentVersionWarning
import warnings

warnings.simplefilter("ignore", category=InconsistentVersionWarning)

class PredictionService:
    def __init__(self):
        self.model = self.load_model()
        self.tfidf_vectorizer = joblib.load('./model/tfidf_vectorizer.joblib')  # Load the TF-IDF vectorizer

    def load_model(self):
        model_path = './model/rf_model.joblib'
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

    def predict(self, question_id, comprehension, question, question_score, examiner_answer):
        if self.model is None:
            print("Model attribute is not initialized. Skipping prediction.")
            return None

        # Preprocess the input features
        input_text = f"{comprehension} {question} {examiner_answer}"
        preprocessed_text = self.preprocess_text(input_text)

        # Vectorize the preprocessed text using the loaded TF-IDF vectorizer
        input_data = self.tfidf_vectorizer.transform([preprocessed_text])

        try:
            # Predict using the model
            prediction = self.model.predict(input_data)
            return prediction[0]  # Assuming a single prediction is made
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
