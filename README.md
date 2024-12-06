## PDF Extraction Tool

This project provides a robust Python-based tool for extracting structured content from PDF documents. The tool leverages the [unstructured.io](https://unstructured.io/) framework to extract text, images, tables, and metadata efficiently. It also includes a setup script for preparing the development environment.

### Features

- **Text Extraction:** Extracts textual content, including titles and paragraphs, from PDF files.
- **Image Extraction:** Extracts embedded images and saves them in a specified directory.
- **Table Extraction:** Extracts tables and provides their textual and HTML representations.
- **Metadata Extraction:** Collects comprehensive metadata for every extracted element.
- **Scalable Output:** Organizes extracted content into directories for easy access.

### Installation

#### Prerequisites
- Python 3.9 or higher
- Ubuntu/Linux (recommended; supports `setup_linux.sh`)
- System dependencies such as `poppler-utils`, `tesseract`, and `ImageMagick`.

#### Step-by-Step Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/pdf-extractor.git
   cd pdf-extractor
   ```

2. **Run the Setup Script:**
   ```bash
   bash setup_linux.sh
   ```
   This script installs system dependencies, sets up a virtual environment, and installs required Python packages.

3. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Verify Installation:**
   Run the verification script:
   ```bash
   python -c "import torch; print('PyTorch version:', torch.__version__)"
   ```

### Usage

1. **Basic Example:**
   Use the `PDFExtractor` class to extract content from a PDF file:
   ```python
   from pdf_extract import PDFExtractor
   
   extractor = PDFExtractor(output_base_dir="extracted_pdfs")
   stats = extractor.extract_content(
       pdf_path="example.pdf",
       strategy="hi_res",
       extract_images=True,
       extract_tables=True
   )
   print("Extraction completed. Stats:", stats)
   ```

2. **Command Line Execution:**
   Modify the `main()` function in `pdf_extract.py` to specify your PDF file path and desired options, then run:
   ```bash
   python pdf_extract.py
   ```

3. **Output Directory Structure:**
   Extracted content will be saved in a structured directory under `extracted_pdfs/<PDF Name>/`:
   - `text/`: Textual content as `.txt` files.
   - `images/`: Extracted images.
   - `tables/`: Tables as `.txt` and `.html` files.
   - `document_metadata.json`: Metadata for all extracted elements.

### Dependencies

- [unstructured.io](https://github.com/Unstructured-IO/unstructured)
- PyTorch
- Detectron2
- OpenCV
- PDF-related tools: `poppler-utils`, `pdf2image`, `tesseract`.

### Contributing

Contributions are welcome! Please fork the repository and create a pull request with your enhancements or fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.
