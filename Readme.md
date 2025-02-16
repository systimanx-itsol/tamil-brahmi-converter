# English → Tamil → Brahmi Converter

## Overview

This project is a web application that allows users to convert text from English to Tamil and then to Tamil-Brahmi script. The application provides a user-friendly interface for inputting text and viewing the converted results in real-time.

## DEMO

https://youtu.be/D6c7k4TtcUk

## Features

- **English to Tamil Conversion**: Input English text and get the corresponding Tamil text.
- **Tamil to Brahmi Conversion**: Convert Tamil text into Brahmi script.
- **Live Conversion Steps**: View the conversion steps dynamically as you input text.
- **Thanglish Support**: Convert Thanglish (English-like Tamil) into Tamil script.
- **Responsive Design**: The application is designed to be responsive and works well on various devices.

## Technologies Used

- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Backend**: Python (FastAPI)


## Installation

To run this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/systimanx-itsol/tamil-brahmi-converter.git
   cd tamil-brahmi-converter
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload

   #or
   # Run on all interfaces
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Open your browser** and go to `http://127.0.0.1:8000`.

## Usage

1. Enter the English text in the provided input box.
2. Click on the "English → Tamil" button to convert the text.
3. The converted Tamil text will appear in the output box.
4. You can also convert Tamil text to Brahmi by entering it in the respective input box and clicking the "Tamil → Brahmi" button.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors and the community for their support.
- Special thanks to the developers of FastAPI and Tailwind CSS for their amazing frameworks.
