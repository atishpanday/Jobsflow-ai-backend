from utils.llm import openai_model, non_streaming_model


class AI_Interviewer:
    def __init__(self):
        self.model = non_streaming_model
        self.prompt = ""

    def append_to_prompt(self, text):
        self.prompt += text

    def get_response(self):
        response = self.model.invoke(
            f"Only reply to the following text in less than 100 words. Keep it concise: \n{self.prompt}"
        ).content
        return response

    def reset_prompt(self):
        self.prompt = ""
