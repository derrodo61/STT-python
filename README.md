# STT-python
A speech-to-text app in Python made with Cursor.

## Description

STT-python is a simple yet powerful speech-to-text application that allows users to convert spoken words into written text. This project leverages Python's capabilities and is developed using the Cursor IDE, demonstrating the ease of creating AI-assisted applications.

## Features

- Real-time speech-to-text conversion
- Support for multiple languages (to be implemented)
- Easy-to-use command-line interface
- Exportable text output

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/STT-python.git
   cd STT-python
   ```

2. Create a virtual environment:

   Option A: Using Python's venv
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

   Option B: Using Conda
   ```bash
   conda create -n stt-python python=3.9
   conda activate stt-python
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the necessary API key:
   - Sign up for an account at [OpenAI](https://openai.com/)
   - Navigate to your API keys page and create a new API key
   - Open the `stt_module.py` file in your project directory
   - Replace the placeholder API key with your actual OpenAI API key:
     ```python
     openai.api_key = "YOUR_OPENAI_API_KEY_HERE"
     ```

   Note: Keep your API key confidential and never share it publicly. Consider using environment variables for added security.

## Usage

To start the speech-to-text conversion:

1. Run the script:
    ```bash
    python stt_module.py
    ```

2. Follow the on-screen instructions to start and stop the recording.

3. The converted text will be displayed and can be exported to a file.

## Contributing

