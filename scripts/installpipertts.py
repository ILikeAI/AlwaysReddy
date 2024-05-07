import os
import platform
import shutil
import tarfile
import zipfile
import requests

def download_file(url, save_path):
    print(f"Downloading from {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length', 0))
        dl = 0
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / total_length)
                    print(f"\r[{'=' * done}{' ' * (50-done)}] {dl/total_length*100:.2f}%", end='')
    print("\nDownload complete.")

def extract_tar_gz(file_path, destination_dir):
    print(f"Extracting {file_path}")
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=destination_dir)
    print("Extraction complete.")

def extract_zip(file_path, destination_dir):
    print(f"Extracting {file_path}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(destination_dir)
    print("Extraction complete.")

def setup_piper_tts():
    operating_system = platform.system()
    machine = platform.machine()
    url_base = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"
    binary_file, binary_name, extract_func = None, None, None

    if operating_system == "Windows":
        binary_file = "piper_windows_amd64.zip"
        extract_func = extract_zip
    elif operating_system == "Darwin":
        if machine == "x86_64":
            binary_file = "piper_macos_x64.tar.gz"
        elif machine == "arm64":
            binary_file = "piper_macos_aarch64.tar.gz"
        else:
            raise ValueError(f"Unsupported macOS architecture: {machine}")
        extract_func = extract_tar_gz
    elif operating_system == "Linux":
        if machine == "x86_64":
            binary_file = "piper_linux_x86_64.tar.gz"
        elif machine == "aarch64":
            binary_file = "piper_linux_aarch64.tar.gz"
        elif machine == "armv7l":
            binary_file = "piper_linux_armv7l.tar.gz"
        else:
            raise ValueError(f"Unsupported Linux architecture: {machine}")
        extract_func = extract_tar_gz
    else:
        raise ValueError(f"Unsupported operating system: {operating_system}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    binary_path = os.path.join(script_dir, binary_file)
    extraction_dir = os.path.join(script_dir, "piper_tts_extracted")
    destination_dir = os.path.join(parent_dir, "piper_tts")  # updated this line


    # Download the binary
    download_url = url_base + binary_file
    download_file(download_url, binary_path)

    # Extract and setup binary
    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    extract_func(binary_path, extraction_dir)

    first_dir_path = next((os.path.join(extraction_dir, d) for d in os.listdir(extraction_dir) if os.path.isdir(os.path.join(extraction_dir, d))), None)
    if not first_dir_path:
        raise Exception("No directory found within the extracted archive.")

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Handle existing directories
    for item in os.listdir(first_dir_path):
        source_item_path = os.path.join(first_dir_path, item)
        destination_item_path = os.path.join(destination_dir, item)
        if os.path.isfile(source_item_path):
            shutil.copy(source_item_path, destination_item_path)
        elif os.path.isdir(source_item_path):
            if os.path.exists(destination_item_path):
                shutil.rmtree(destination_item_path)
            shutil.copytree(source_item_path, destination_item_path)

    # Clean up the extraction directory and the downloaded binary file
    shutil.rmtree(extraction_dir)
    os.remove(binary_path)

    print("Piper TTS setup completed successfully.")
