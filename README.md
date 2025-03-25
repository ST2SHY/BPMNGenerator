# BPMN Code Generation and Verification Framework

> ⚠️ *Note: This documentation is still being updated.*

## Project Overview
This repository implements a BPMN code generation and verification framework based on Large Language Models (LLMs).  
The core functionalities include:
- **BPMN Generation**: Use LLMs to generate BPMN-related components.
- **Model Verification**: Use verification tools to validate the quality of generated BPMN models.

## Repository Structure
```
.
├── generation/        # Scripts for generating BPMN components
├── verification/      # Scripts for invoking verification tools
├── .secret            # File storing the GPT API key (must be created manually)
├── README.md          # Project documentation
```

### `generation/`
This folder contains a series of Python scripts for generating BPMN components.

### `verification/`
This folder contains Python scripts that call verification tools to check the correctness of BPMN models.

### `.secret`
This file stores the GPT API key, allowing access to the API during the generation process.  
> **Note**: This file should **not** be committed to version control systems (like Git). Be sure to add `.secret` to your `.gitignore` file to avoid exposing sensitive information.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
