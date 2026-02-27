class InferenceMethod:
    def infer(self, policy_text):
        raise NotImplementedError("Subclasses should implement this method.")

    def get_audit_info(self):
        raise NotImplementedError("Subclasses should implement this method.")