# Multilingual Translator

![Multilingual Translator](translator_logo.png)

## Overview

This project is a multilingual translator application that utilizes various functionalities including text-to-speech (TTS), speech-to-text (STT), and image-to-text (OCR). It provides a convenient way to translate between different languages using both textual and spoken input/output methods.

## Features

- **Text-to-Speech (TTS):** Convert text in one language to spoken audio output in another language.
- **Speech-to-Text (STT):** Recognize spoken input and convert it into text in the desired language.
- **Image-to-Text (OCR):** Extract text from images and translate it into the desired language.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your_username/multilingual-translator.git
   cd multilingual-translator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Ensure you have Python 3.6+ installed.

## Usage

### Text-to-Speech (TTS)

1. Run the text-to-speech translator:
   ```
   python text_to_speech.py --input "Hello, how are you?" --language "en"
   ```
   Replace `"Hello, how are you?"` with your desired text and `"en"` with the target language code (e.g., `"fr"` for French).

### Speech-to-Text (STT)

1. Run the speech-to-text translator:
   ```
   python speech_to_text.py --language "en"
   ```
   Speak your text in the specified language ("en" for English). The script will output the recognized text.

### Image-to-Text (OCR)

1. Run the image-to-text translator:
   ```
   python image_to_text.py --image_path "path_to_image.jpg" --language "en"
   ```
   Replace `"path_to_image.jpg"` with the path to your image file and `"en"` with the language code of the text in the image.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository and create your branch from `main`.
2. Make your changes and ensure the code lints.
3. Create a pull request with a detailed description of your changes.

