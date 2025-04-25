from google import genai

class RAG:
    def __init__(self, api_key, model="gemini-1.5-flash", max_tokens=1000):
        """
        Initialize the RAG (Retrieval-Augmented Generation) pipeline with Google Gemini.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def query_gemini(self, context, query):
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"

        # Send the request and get the response
        response = self._send_request(prompt)
        if response:
            return response.text.strip()  # Stripping any extra whitespace
        return None

    def _send_request(self, prompt):
        """
        Send a request to the Gemini model API with the given prompt.
        """
        try:
            # Send the request to generate content using the Gemini model
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response
        except Exception as e:
            print(f"Error querying the model: {e}")
            return None

    def generate_answer(self, query, context):
        """
        Generate an answer using the RAG pipeline by querying Gemini.
        """
        return self.query_gemini(context, query)
