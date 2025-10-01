# QFIL Downloader Configuration

# Flask Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
DEBUG = True

# Application Settings
HOST = "0.0.0.0"
PORT = 5000

# Project Structure
PROJECTS_BASE_DIR = "~"  # User home directory
QFIL_SUBDIR = "Unpacking_Tool/qfil_dowload_emmc"

# File Upload Limits (if needed for future features)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB

# Temporary Directory Settings
TEMP_DIR_PREFIX = "qfil_download_"