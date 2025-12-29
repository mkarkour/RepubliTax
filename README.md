# 📑 RepubliTax - Automated Monthly Tax Report

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)

A streamlined tool to automate the processing of Trade Republic tax documents and generate
filled tax forms for Belgian tax authorities.

## 📚 Table of contents

- [🚀 About](#-about)
- [🛠️ Features](#️-features)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [▶️ Usage](#️-usage)
- [🧪 Tests](#-tests)
- [📁 Project structure](#-project-structure)
- [🤝 Contribute](#-contribute)
- [📄 License](#-license)
- [👨‍💻 Authors](#-authors)
- [🔗 Resources](#-resources)

## 🚀 About

RepubliTax is an advanced tool designed to simplify the process of filing tax reports for
Trade Republic users in Belgium. The application automatically extracts data from Trade
Republic PDF tax documents and fills out the appropriate Belgian tax forms, saving users
time and ensuring accuracy in their tax reporting.

The tool leverages modern technologies such as Streamlit for a user-friendly interface,
PyMuPDF for PDF processing, and Pandas for data management, all while keeping your 
sensitive financial data secure by processing everything locally on your machine.

## 🛠️ Features

- **PDF Content Extraction**: Automatically extracts transaction data from Trade Republic tax documents
- **Data Validation**: Ensures all extracted data is properly formatted and complete
- **Form Auto-filling**: Fills Belgian tax forms with the extracted data
- **Document Signing**: Option to add your digital signature to the completed form
- **Document Preview**: Preview the filled form before downloading
- **Email Integration**: Send the completed document directly via email
- **Secure Processing**: All data processing happens locally on your machine
- **Multi-page Support**: Process tax documents with multiple pages
- **User-friendly Interface**: Simple and intuitive web interface

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Docker (optional)

### Option 1: Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RepubliTax.git
cd RepubliTax
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RepubliTax.git
cd RepubliTax
```

2. Make the Docker script executable:
```bash
chmod +x run_docker.sh
```

3. Run the Docker script:
```bash
./run_docker.sh
```

4. Follow the prompts to either:
   - Run the application on port 8501
   - Open an interactive terminal in the container

## ⚙️ Configuration

### Required Files

1. **Form Template**: Place your blank tax form template at `docs/form.pdf` (or upload it 
via the interface)
2. **Signature**: Your signature image should be placed at `docs/signature.png` (or upload 
it via the interface)

### Directory Structure

The application expects the following directory structure:
```
RepubliTax/
├───docs/           # Stores form templates and signature
├───output/         # Generated output files will be stored here
├───src/            # Core processing code
└───app/            # Core application code
```

## ▶️ Usage

1. **Start the application**:
```bash
streamlit run app/app.py
```
or
```bash
python launcher.py
```

2. **Access the application**:
   - Open your browser and navigate to http://localhost:8501

3. **Using the interface**:
![User Interface](docs/assets/user_interface.png)
*Screenshot of the RepubliTax user interface*
   - Upload your Trade Republic tax document
   - Enter your Belgian national number
   - (Optional) Add your signature
   - Click "Validate infos" to process the document
   - Review the extracted data
   - Preview the filled form
   - Download the completed form or send it via email

## 🧪 Tests

To run the tests:

```bash
python -m pytest test/
```

## 📁 Project structure

```
RepubliTax/
├───.vscode/          # VS Code configuration
├───app/              # Streamlit application
│   └───__pycache__
├───docs/             # Document templates and signature
├───output/           # Generated forms
├───src/              # Core functionality
│   └───__pycache__
├───test/             # Test files
│   └───__pycache__
└───__pycache__
```

### Key Files

- `app/Home.py`: Main Streamlit application
- `src/reader.py`: PDF content extraction functionality
- `src/writer.py`: PDF form filling functionality
- `src/utils_files.py`: Utility functions for file handling
- `run_docker.sh`: Script to build and run the Docker container

## 🤝 Contribute

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Authors

- **mkarkour** - *Initial work* - [GitHub Profile](https://github.com/mkarkour)

## 🔗 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Trade Republic Help Center](https://support.traderepublic.com/)