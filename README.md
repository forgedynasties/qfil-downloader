# QFIL Downloader

A Flask-based web application for managing and downloading QFIL packages from AOSP projects.

## Features

- 🚀 **Web Interface**: Clean, responsive web interface for browsing projects
- ⚙️ **Manual Project Management**: Add and manage AOSP project paths via web interface
- 📦 **Automatic Packaging**: Automatically zips QFIL directories for download
- � **Real-time Progress**: Live zipping progress with file-by-file tracking
- �🔒 **Secure Downloads**: Validates project names and paths for security
- 🧹 **Temporary File Management**: Automatically cleans up temporary files after download
- � **Project Details**: View file listings, sizes, and descriptions before downloading
- 🌐 **API Support**: JSON API endpoints for programmatic access
- 🎯 **Flexible Paths**: Support for projects located anywhere on the system

## Installation

### Option 1: Docker (Recommended)

1. **Using Docker Compose:**
   ```bash
   # Update docker-compose.yml with your AOSP project paths
   docker-compose up -d
   ```
   
2. **Access the application:**
   Open http://localhost:5000

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

### Option 2: Local Python Installation

1. **Clone or download this project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up project structure in your home directory**:
   ```
   ~/ (User Home Directory)
   ├── project1/                    # Your AOSP projects go here
   │   └── Unpacking_Tool/
   │       └── qfil_dowload_emmc/   # QFIL files go here
   ├── project2/
   │   └── Unpacking_Tool/
   │       └── qfil_dowload_emmc/
   └── ...
   
   qfil-downloader/ (Application Directory)
   ├── app.py
   ├── requirements.txt
   └── templates/
   ```

## Usage

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   Open your browser to `http://localhost:5000`

3. **Add AOSP projects**:
   - Navigate to "Manage Projects" in the web interface
   - Click "Add New Project" to add project paths
   - Each project must have the structure: `/path/to/project/Unpacking_Tool/qfil_dowload_emmc/`
   - The QFIL files should be placed in the `qfil_dowload_emmc` directory

## Project Structure

```
your-project-name/
└── Unpacking_Tool/
    └── qfil_dowload_emmc/
        ├── file1.bin
        ├── file2.mbn
        └── ...
```

## API Endpoints

- `GET /` - Main web interface
- `GET /manage` - Project management interface  
- `GET /api/projects` - JSON list of available projects
- `POST /add_project` - Add new project path
- `DELETE /remove_project/<name>` - Remove project
- `GET /download/<project_name>` - Download QFIL package as ZIP
- `GET /progress/<download_id>` - Get download/zipping progress
- `GET /project/<project_name>` - Project details page

## Configuration

The application can be configured by modifying variables in `app.py`:

- `PROJECTS_FILE`: JSON file storing project configurations (default: `projects.json`)
- `QFIL_SUBDIR`: Subdirectory path within each project (default: `Unpacking_Tool/qfil_dowload_emmc`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `5000`)

Project paths are managed through the web interface and stored in `projects.json`.

## Security Features

- Project name validation (alphanumeric characters, hyphens, underscores, dots only)
- Path traversal protection
- Temporary file cleanup
- Error handling for invalid requests

## Development

To run in development mode:
```bash
python app.py
```

For production deployment, consider using:
- Gunicorn or uWSGI as WSGI server
- Nginx as reverse proxy
- Environment variables for configuration

## License

This project is provided as-is for educational and development purposes.