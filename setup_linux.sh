#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        # Get Python version
        version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        # Compare versions
        if [ "$(echo -e "3.7\n$version" | sort -V | head -n1)" = "3.7" ]; then
            return 0
        fi
        return 1
    fi
    return 2
}

# Function to install system dependencies
install_system_dependencies() {
    print_message "Installing system dependencies..." "${YELLOW}"
    
    # Update package list
    sudo apt-get update
    
    # Install required system packages
    sudo apt-get install -y \
        python3-pip \
        python3-dev \
        python3-venv \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        libmagic1 \
        libpoppler-cpp-dev \
        pkg-config \
        cmake \
        build-essential \
        libgl1-mesa-glx \
        libglib2.0-0 \
        wget \
        git \
        imagemagick \
        ghostscript
        
    if [ $? -eq 0 ]; then
        print_message "System dependencies installed successfully." "${GREEN}"
    else
        print_message "Error installing system dependencies." "${RED}"
        exit 1
    fi

    # Configure ImageMagick to allow PDF operations
    if [ -f "/etc/ImageMagick-6/policy.xml" ]; then
        sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml
    fi
    
    if [ -f "/etc/ImageMagick-7/policy.xml" ]; then
        sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-7/policy.xml
    fi
    
    # Verify ImageMagick installation
    if command_exists convert; then
        print_message "ImageMagick installed successfully." "${GREEN}"
    else
        print_message "Error: ImageMagick installation failed." "${RED}"
        exit 1
    fi
}

# Function to create and activate virtual environment
setup_virtual_environment() {
    print_message "Setting up Python virtual environment..." "${YELLOW}"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    if [ $? -eq 0 ]; then
        print_message "Virtual environment created and activated successfully." "${GREEN}"
    else
        print_message "Error setting up virtual environment." "${RED}"
        exit 1
    fi
}

# Function to install Python dependencies

# Modified install_python_dependencies function
install_python_dependencies() {
    print_message "Installing Python dependencies..." "${YELLOW}"

    # Install build essentials first
    print_message "Installing build essentials..." "${YELLOW}"
    pip install --upgrade pip setuptools wheel
    
    # First install PyTorch and its dependencies
    print_message "Installing PyTorch and dependencies..." "${YELLOW}"
    pip install future typing_extensions packaging ninja cython
    pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121
    
    if [ $? -eq 0 ]; then
        print_message "PyTorch installed successfully." "${GREEN}"
    else
        print_message "Error installing PyTorch." "${RED}"
        exit 1
    fi
    
    # Install core AI dependencies
    print_message "Installing core AI dependencies..." "${YELLOW}"
    pip install opencv-python>=4.8.0 'git+https://github.com/facebookresearch/detectron2.git'
    
    if [ $? -eq 0 ]; then
        print_message "Core AI dependencies installed successfully." "${GREEN}"
    else
        print_message "Error installing core AI dependencies." "${RED}"
        exit 1
    fi
    
    # Create requirements.txt with remaining dependencies
    cat > requirements.txt << EOL
unstructured[all-docs]>=0.16.5
unstructured-inference>=0.8.1
pdf2image>=1.17.0
pdfminer.six>=20240706 
pypdf>=5.1.0
Pillow>=11.0.0
numpy>=1.24.0
pi-heif>=0.7.1
python-magic>=0.4.27
pytesseract>=0.3.10
EOL

    # Install remaining dependencies
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_message "Remaining Python dependencies installed successfully." "${GREEN}"
    else
        print_message "Error installing remaining Python dependencies." "${RED}"
        exit 1
    fi
    
    # Install additional unstructured extras
    print_message "Installing unstructured extras..." "${YELLOW}"
    pip install "unstructured[local-inference]" "unstructured[all-docs]"
    
    if [ $? -eq 0 ]; then
        print_message "Unstructured extras installed successfully." "${GREEN}"
    else
        print_message "Error installing unstructured extras." "${RED}"
        exit 1
    fi
}


# Function to verify installations
verify_installation() {
    print_message "Verifying installations..." "${YELLOW}"
    
    # Check system dependencies
    local missing_deps=()
    
    for cmd in python3 tesseract convert pkg-config; do
        if ! command_exists $cmd; then
            missing_deps+=($cmd)
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_message "Missing system dependencies: ${missing_deps[*]}" "${RED}"
        return 1
    fi
    
    # Verify Python packages
    python3 << EOL
import sys
try:
    import unstructured
    import pdf2image
    import pdfminer
    import PIL
    import numpy
    import cv2
    import torch
    import detectron2
    print("All Python packages verified successfully!")
    sys.exit(0)
except ImportError as e:
    print(f"Error importing package: {str(e)}")
    sys.exit(1)
EOL
    
    if [ $? -eq 0 ]; then
        print_message "All installations verified successfully!" "${GREEN}"
        return 0
    else
        print_message "Some Python packages could not be verified." "${RED}"
        return 1
    fi
}

# Main installation process
main() {
    print_message "Starting installation process..." "${YELLOW}"
    
    # Check Python version
    if ! check_python_version; then
        print_message "Python 3.7 or higher is required. Current version is: $(python3 --version)" "${RED}"
        exit 1
    fi
    
    # Install dependencies
    install_system_dependencies
    setup_virtual_environment
    install_python_dependencies
    
    # Verify installation
    if verify_installation; then
        print_message "\nInstallation completed successfully! 🎉" "${GREEN}"
        print_message "\nTo activate the virtual environment, run:" "${YELLOW}"
        print_message "source venv/bin/activate" "${NC}"
    else
        print_message "\nInstallation completed with some issues. Please check the error messages above." "${RED}"
        exit 1
    fi
}

# Run main installation
main