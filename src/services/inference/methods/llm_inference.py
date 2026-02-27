from src.services.inference.methods.base import InferenceMethod
from src.services.llm.client import LLMClient

class LLMInference(InferenceMethod):
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or "mock"
        self.llm_client = LLMClient(endpoint=self.endpoint)


    def infer(self, policy_text):
        response = self.llm_client.query(policy_text)
        inferred_codes = self.process_response(response)
        return inferred_codes

    def process_response(self, response):
        inferred_codes = []
        for code_info in response.get('codes', []):
            inferred_code = {
                'code': code_info['code'],
                'confidence': code_info['confidence'],
                'justification': code_info['justification']
            }
            inferred_codes.append(inferred_code)
        
        audit_info = {
            'method': 'LLM',
            'input_text': response.get('input_text'),
            'timestamp': response.get('timestamp')
        }
        
        return {
            'inferred_codes': inferred_codes,
            'audit': audit_info
        }