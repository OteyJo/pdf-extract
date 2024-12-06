import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Union, IO
from io import BytesIO, TextIOWrapper, BufferedReader
from tempfile import SpooledTemporaryFile

# Import unstructured components
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import (
    Text,
    Title,
    Image,
    Table,
    Element
)

def convert_to_bytes(
    file: Optional[Union[bytes, SpooledTemporaryFile, IO[bytes]]] = None,
) -> bytes:
    """Convert various file-like objects to bytes."""
    if isinstance(file, bytes):
        f_bytes = file
    elif isinstance(file, SpooledTemporaryFile):
        file.seek(0)
        f_bytes = file.read()
        file.seek(0)
    elif isinstance(file, BytesIO):
        f_bytes = file.getvalue()
    elif isinstance(file, (TextIOWrapper, BufferedReader)):
        with open(file.name, "rb") as f:
            f_bytes = f.read()
    else:
        raise ValueError("Invalid file-like object type")
    return f_bytes

class PDFExtractor:
    """A class to extract content from PDFs using unstructured.io framework."""
    
    def __init__(self, output_base_dir: str = "extracted_content"):
        """
        Initialize the PDF extractor.
        
        Args:
            output_base_dir (str): Base directory for extracted content
        """
        self.output_base_dir = output_base_dir
        
    def _create_output_dirs(self, pdf_name: str) -> tuple[Path, Path, Path, Path]:
        """Create output directories for the extracted content."""
        # Create main directory named after the PDF
        base_dir = Path(self.output_base_dir) / pdf_name
        
        # Create subdirectories for different content types
        text_dir = base_dir / "text"
        images_dir = base_dir / "images"
        tables_dir = base_dir / "tables"
        metadata_dir = base_dir / "metadata"
        
        # Create all directories
        for dir_path in [base_dir, text_dir, images_dir, tables_dir, metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return base_dir, text_dir, images_dir, tables_dir
    
    def _process_element(self, 
                        element: Element, 
                        index: int,
                        text_dir: Path,
                        tables_dir: Path,
                        pdf_path: str) -> Dict[str, Any]:
        """Process a single element and extract its metadata."""
        metadata = {
            "element_index": index,
            "element_type": element.__class__.__name__,
            "filename": os.path.basename(pdf_path),
            "extraction_date": datetime.now().isoformat()
        }
        
        try:
            # Extract element metadata
            if hasattr(element, "metadata"):
                metadata.update(self._extract_element_metadata(element))
            
            # Process element based on its type
            if isinstance(element, (Text, Title)):
                output_path = text_dir / f"{element.__class__.__name__.lower()}_{index}.txt"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(element.text)
                metadata["content_path"] = str(output_path)
                
            elif isinstance(element, Table):
                # Save table content
                txt_path = tables_dir / f"table_{index}.txt"
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(element.text)
                metadata["content_path"] = str(txt_path)
                
                # Save HTML structure if available
                if hasattr(element.metadata, "text_as_html") and element.metadata.text_as_html:
                    html_path = tables_dir / f"table_{index}.html"
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(element.metadata.text_as_html)
                    metadata["html_path"] = str(html_path)
                    
            elif isinstance(element, Image):
                if hasattr(element.metadata, "image_path"):
                    metadata["image_path"] = element.metadata.image_path
                    
        except Exception as e:
            print(f"Warning: Error processing element {index}: {str(e)}")
            
        return metadata
    
    def _extract_element_metadata(self, element: Element) -> Dict[str, Any]:
        """Extract metadata from an element."""
        metadata = {}
        
        if hasattr(element.metadata, "coordinates"):
            coords = element.metadata.coordinates
            if coords and hasattr(coords, "points"):
                metadata["coordinates"] = {
                    "points": coords.points,
                    "system": str(coords.system) if hasattr(coords, "system") else None
                }
        
        for field in [
            "page_number", "page_name", "languages", "links", "link_urls",
            "link_texts", "url", "category_depth", "section", "text_as_html",
            "emphasized_text_contents", "emphasized_text_tags", "image_path",
            "detection_class_prob"
        ]:
            if hasattr(element.metadata, field):
                value = getattr(element.metadata, field)
                if value is not None:
                    metadata[field] = value
        
        return metadata
    
    def extract_content(self, 
                       pdf_path: str, 
                       strategy: str = "hi_res",
                       extract_images: bool = True,
                       extract_tables: bool = True) -> dict:
        """Extract content from a PDF file."""
        # Get PDF name without extension
        pdf_name = Path(pdf_path).stem
        
        # Create output directories
        base_dir, text_dir, images_dir, tables_dir = self._create_output_dirs(pdf_name)
        
        # Configure extraction types
        extract_types = []
        if extract_images:
            extract_types.append("Image")
        if extract_tables:
            extract_types.append("Table")
            
        try:
            # Extract content using unstructured
            elements = partition_pdf(
                filename=pdf_path,
                strategy=strategy,
                extract_image_block_types=extract_types,
                extract_image_block_output_dir=str(images_dir),
                infer_table_structure=True
            )
            
            # Initialize statistics
            stats = {
                "text_blocks": 0,
                "titles": 0,
                "images": 0,
                "tables": 0
            }
            
            all_metadata = []
            
            # Process each element
            for idx, element in enumerate(elements):
                metadata = self._process_element(
                    element, idx, text_dir, tables_dir, pdf_path
                )
                all_metadata.append(metadata)
                
                # Update statistics
                if isinstance(element, Title):
                    stats["titles"] += 1
                elif isinstance(element, Text):
                    stats["text_blocks"] += 1
                elif isinstance(element, Image):
                    stats["images"] += 1
                elif isinstance(element, Table):
                    stats["tables"] += 1
                    
            # Save document metadata
            document_metadata = {
                "filename": os.path.basename(pdf_path),
                "extraction_date": datetime.now().isoformat(),
                "statistics": stats,
                "elements_metadata": all_metadata
            }
            
            with open(base_dir / "document_metadata.json", "w", encoding="utf-8") as f:
                json.dump(document_metadata, f, indent=2, ensure_ascii=False)
                
            return stats
            
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return {}

def main():
    # Example usage
    try:
        extractor = PDFExtractor("extracted_pdfs")
        
        # Extract content from a PDF
        pdf_path = "your_pdf_here"  # Replace with your PDF path
        results = extractor.extract_content(
            pdf_path,
            strategy="hi_res",
            extract_images=True,
            extract_tables=True
        )
        
        print("\nExtraction completed successfully! 🎉")
        print("\nStatistics:")
        for key, value in results.items():
            if isinstance(value, (int, str, float)):  # Only print simple values
                print(f"- {key}: {value}")
                
        print("\nExtracted content is saved in:", 
              Path("extracted_pdfs") / Path(pdf_path).stem)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
