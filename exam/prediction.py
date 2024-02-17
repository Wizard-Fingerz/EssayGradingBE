import joblib  # or any other library you used to dump the model
import numpy as np


class PredictionService:
    def __init__(self, model_path):
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            raise ValueError(f"Error loading the model from {model_path}: {e}")

    def predict(self, question_id, comprehension, question_score, examiner_answer, student_answer, student_score ):
        # Preprocess the input features if necessary
        input_data = (question_id, comprehension, question_score, student_answer, examiner_answer, student_score)
        input_data = np.array(input_data)  # Ensure input_data is a numpy array
        try:
            # Predict using the model
            prediction = self.model.predict(input_data)
            return prediction[0]  # Assuming a single prediction is made
        except Exception as e:
            raise ValueError(f"Error making prediction: {e}")
