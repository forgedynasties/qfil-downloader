# QFIL Downloader - Usage Instructions

## Quick Start

1. **The server is already running!** 
   - Access the web interface at: http://localhost:5000
   - The server runs on all network interfaces (0.0.0.0:5000)

2. **Adding AOSP Projects in Home Directory:**
   ```
   ~/ (Your Home Directory)
   ├── your_project_name/
   │   └── Unpacking_Tool/
   │       └── qfil_dowload_emmc/
   │           ├── boot.img
   │           ├── system.img
   │           └── other_qfil_files...
   ```

3. **Network Access:**
   - Local access: http://localhost:5000
   - Network access: http://your-server-ip:5000
   - Other devices can access the web app using your server's IP

## File Structure Requirements

Each AOSP project must follow this exact structure in your home directory:
```
~/ (Home Directory)
└── [project_name]/
    └── Unpacking_Tool/
        └── qfil_dowload_emmc/
            └── [QFIL files here]
```

## Features Available

✅ **Web Interface** - Browse projects via web browser
✅ **Automatic Zipping** - Downloads are automatically packaged as ZIP files  
✅ **Temporary File Cleanup** - Server cleans up temporary files after download
✅ **Project Details** - View file listings before downloading
✅ **JSON API** - Programmatic access via `/api/projects`
✅ **Security** - Input validation and path traversal protection

## API Endpoints

- `GET /` - Main web interface
- `GET /api/projects` - JSON list of available projects
- `GET /download/<project_name>` - Download QFIL package as ZIP
- `GET /project/<project_name>` - Project details page

## Example: Adding a New Project

1. Create project directory in your home directory:
   ```bash
   mkdir -p "~/my_device_project/Unpacking_Tool/qfil_dowload_emmc"
   ```

2. Add your QFIL files to:
   ```
   ~/my_device_project/Unpacking_Tool/qfil_dowload_emmc/
   ```

3. Refresh the web page - your project will appear automatically!

## Development Commands

- **Start server**: `python app.py` (already running via task)
- **Install dependencies**: `pip install -r requirements.txt`
- **Stop server**: Press `Ctrl+C` in the terminal

The application is production-ready and can be accessed by other devices on your network!