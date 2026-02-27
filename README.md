# HCPCS Inference Service

## Overview
The HCPCS Inference Service is designed to infer HCPCS codes from policy text using various inference methods, including Large Language Models (LLM) and Retrieval-Augmented Generation (RAG). The service is built to be extensible, allowing for the integration of additional inference methods in the future.

## API Contract

### Input
- **Policy Text**: The text from which HCPCS codes will be inferred.

### Returns
- **Inferred HCPCS Codes**: A list of HCPCS codes inferred from the policy text.
- **Confidence Scores**: A confidence score between 0 and 1 for each inferred code, indicating the reliability of the inference.
- **Justification**: A brief explanation of why each code was inferred.
- **Audit/Provenance Object**: An object that provides details on the inference process, allowing for reproducibility and auditing.

## Running the Pipeline
To run the inference service, use the following command:

```bash
python run_pipeline.py --input policy_snippets.csv --output inferred_codes.json
```

### Parameters
- `--input`: Path to the input file containing policy text (CSV format).
- `--output`: Path to the output file where inferred HCPCS codes will be saved (JSON format).

## Directory Structure
- `src/`: Contains the source code for the inference service.
  - `services/`: Contains the service logic, including inference methods and orchestration.
  - `models/`: Contains data schemas for the inference results.
  - `utils/`: Contains utility functions for logging and other common tasks.
- `run_pipeline.py`: The main entry point for executing the inference service.
- `requirements.txt`: Lists the dependencies required for the project.
- `inferred_codes.json`: The expected output file containing the results of the inference process.
- `README.md`: Documentation for the project.

## Future Enhancements
In future versions, the service will support multiple inference methods. The API and data schemas will be designed to accommodate these changes without breaking existing consumers. This will include versioning of the API and the ability to specify the inference method used for each request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.