import joblib  # or any other library you used to dump the model

class PredictionService:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, question_id, comprehension, question_score, answer, examiner_answer):
        # Preprocess the input features if necessary
        input_data = [[question_id, comprehension, question_score, answer, examiner_answer]]
        prediction = self.model.predict(input_data)
        return prediction[0]  # Assuming a single prediction is made
