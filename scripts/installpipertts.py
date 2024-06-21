import os
import sys
import platform
import shutil
import tarfile
import zipfile
import subprocess

def download_file(url, save_path):
    # Install requests library within the virtual environment
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests
    
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
    # Determine the operating system and machine architecture
    operating_system = platform.system()
    machine = platform.machine()

    # Set up URLs and file names based on the GitHub repository
    url_base = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"
    additional_url_base = "https://github.com/rhasspy/piper-phonemize/releases/download/2023.11.14-4/"
    binary_file, binary_name, extract_func = None, None, None
    additional_file = None

    # Determine the correct binary and extraction method based on the OS and architecture
    if operating_system == "Windows":
        binary_file = "piper_windows_amd64.zip"
        extract_func = extract_zip
    elif operating_system == "Darwin":  # macOS
        if machine == "x86_64":
            binary_file = "piper_macos_x64.tar.gz"
            additional_file = "piper-phonemize_macos_x64.tar.gz"
        elif machine == "arm64":
            binary_file = "piper_macos_aarch64.tar.gz"
            additional_file = "piper-phonemize_macos_aarch64.tar.gz"
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

    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    binary_path = os.path.join(script_dir, binary_file)
    additional_path = os.path.join(script_dir, additional_file) if additional_file else None
    extraction_dir = os.path.join(script_dir, "piper_tts_extracted")
    destination_dir = os.path.join(parent_dir, "piper_tts")

    # Download the main binary
    download_url = url_base + binary_file
    download_file(download_url, binary_path)

    # Download the additional file for macOS if needed
    if additional_file:
        additional_url = additional_url_base + additional_file
        download_file(additional_url, additional_path)

    # Create extraction directory
    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    # Extract the main binary
    extract_func(binary_path, extraction_dir)

    # Extract the additional file if downloaded (for macOS)
    if additional_file and additional_path:
        with tarfile.open(additional_path, "r:gz") as tar:
            members = [m for m in tar.getmembers() if 'lib/' in m.name]
            tar.extractall(path=destination_dir, members=members)
        print("Extracted additional files to lib directory.")

    # Find the extracted directory
    first_dir_path = next((os.path.join(extraction_dir, d) for d in os.listdir(extraction_dir) if os.path.isdir(os.path.join(extraction_dir, d))), None)
    if not first_dir_path:
        raise Exception("No directory found within the extracted archive.")

    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Copy files to the destination directory, handling existing files/directories
    for item in os.listdir(first_dir_path):
        source_item_path = os.path.join(first_dir_path, item)
        destination_item_path = os.path.join(destination_dir, item)
        if os.path.isfile(source_item_path):
            shutil.copy(source_item_path, destination_item_path)
        elif os.path.isdir(source_item_path):
            if os.path.exists(destination_item_path):
                shutil.rmtree(destination_item_path)
            shutil.copytree(source_item_path, destination_item_path)

    # Adjust the paths to dylib files using install_name_tool on macOS
    if operating_system == "Darwin":
        piper_executable = os.path.join(destination_dir, "piper")
        lib_dir = os.path.join(destination_dir, "piper-phonemize", "lib")
        dylib_files = ["libespeak-ng.1.dylib", "libpiper_phonemize.1.dylib", "libonnxruntime.1.14.1.dylib"]

        for dylib in dylib_files:
            dylib_path = os.path.join(lib_dir, dylib)
            subprocess.run(["install_name_tool", "-change", f"@rpath/{dylib}", dylib_path, piper_executable], check=True)

    # Clean up temporary files and directories
    shutil.rmtree(extraction_dir)
    os.remove(binary_path)
    if additional_file and additional_path:
        os.remove(additional_path)

    print("Piper TTS setup completed successfully.")

if __name__ == "__main__":
    setup_piper_tts()