import joblib  # or any other library you used to dump the model

class PredictionService:
    def __init__(self, model_path):
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            raise ValueError(f"Error loading the model from {model_path}: {e}")

    def predict(self, comprehension, question_score, answer, examiner_answer):
        # Preprocess the input features if necessary
        input_data = [(comprehension, question_score, answer, examiner_answer)]
        
        try:
            # Predict using the model
            prediction = self.model.predict(input_data)
            return prediction[0]  # Assuming a single prediction is made
        except Exception as e:
            raise ValueError(f"Error making prediction: {e}")
