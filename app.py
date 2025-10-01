#!/usr/bin/env python3
"""
QFIL Downloader - Flask Web Application
Provides a web interface for downloading QFIL packages from AOSP projects
"""

import os
import tempfile
import shutil
import zipfile
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, abort, session
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Configuration
PROJECTS_FILE = 'projects.json'  # File to store manual project paths
QFIL_SUBDIR = 'Unpacking_Tool/qfil_download_emmc'

# Progress tracking for downloads
download_progress = {}
download_lock = threading.Lock()

def load_projects():
    """Load manual project list from JSON file"""
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []

def save_projects(projects):
    """Save project list to JSON file"""
    try:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)
        return True
    except IOError:
        return False

def get_latest_modification_time(qfil_path):
    """Get the latest modification time from all files in the QFIL directory"""
    latest_mtime = 0
    try:
        for file_path in qfil_path.rglob('*'):
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
    except (OSError, IOError):
        pass
    return latest_mtime if latest_mtime > 0 else None

def format_timestamp(timestamp):
    """Format timestamp in human readable format"""
    if timestamp is None:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return "Unknown"

def get_available_projects():
    """Get list of available AOSP projects with QFIL packages"""
    projects = []
    manual_projects = load_projects()
    
    for project_config in manual_projects:
        project_path = Path(project_config['path'])
        qfil_path = project_path / QFIL_SUBDIR
        
        if qfil_path.exists() and qfil_path.is_dir():
            # Check if directory has files
            files = list(qfil_path.glob('*'))
            if files:
                # Get the latest modification time from all files in the QFIL directory
                latest_mtime = get_latest_modification_time(qfil_path)
                
                projects.append({
                    'name': project_config['name'],
                    'path': str(project_path),
                    'qfil_path': str(qfil_path),
                    'file_count': len(files),
                    'size': get_directory_size(qfil_path),
                    'description': project_config.get('description', ''),
                    'last_modified': latest_mtime,
                    'last_modified_formatted': format_timestamp(latest_mtime)
                })
    
    return sorted(projects, key=lambda x: x['name'])

def get_directory_size(path):
    """Calculate total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except (OSError, IOError):
        pass
    return total_size

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

@app.route('/')
def index():
    """Main page showing all available projects"""
    projects = get_available_projects()
    return render_template('index.html', projects=projects, format_size=format_file_size)

@app.route('/api/projects')
def api_projects():
    """API endpoint to get projects list as JSON"""
    projects = get_available_projects()
    return jsonify(projects)

@app.route('/manage')
def manage_projects():
    """Project management page"""
    projects = load_projects()
    return render_template('manage.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    """Add a new project path"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'path' not in data:
        return jsonify({'error': 'Name and path are required'}), 400
    
    # Validate project name (more lenient, but secure)
    name = data['name'].strip()
    if not name or len(name) > 100:
        return jsonify({'error': 'Project name must be between 1-100 characters'}), 400
    
    # Check for dangerous characters that could cause issues
    dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in name for char in dangerous_chars):
        return jsonify({'error': 'Project name contains invalid characters'}), 400
    
    # Validate project path
    project_path = Path(data['path'])
    qfil_path = project_path / QFIL_SUBDIR
    
    if not qfil_path.exists():
        return jsonify({'error': f'QFIL directory not found at: {qfil_path}'}), 400
    
    projects = load_projects()
    
    # Check if project name already exists
    if any(p['name'] == name for p in projects):
        return jsonify({'error': 'Project name already exists'}), 400
    
    new_project = {
        'name': name,
        'path': str(project_path),
        'description': data.get('description', '').strip(),
        'added_date': datetime.now().isoformat()
    }
    
    projects.append(new_project)
    
    if save_projects(projects):
        return jsonify({'success': True, 'project': new_project})
    else:
        return jsonify({'error': 'Failed to save project'}), 500

@app.route('/remove_project/<project_name>', methods=['DELETE'])
def remove_project(project_name):
    """Remove a project from the list"""
    projects = load_projects()
    projects = [p for p in projects if p['name'] != project_name]
    
    if save_projects(projects):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to remove project'}), 500

@app.route('/progress/<download_id>')
def get_progress(download_id):
    """Get download progress for a specific download"""
    with download_lock:
        progress = download_progress.get(download_id, {'progress': 0, 'status': 'not_found'})
    return jsonify(progress)

@app.route('/browse_folders')
def browse_folders():
    """Browse folders for project selection"""
    path = request.args.get('path', '/')
    
    try:
        # Security check - prevent path traversal
        if '..' in path or not os.path.isabs(path):
            return jsonify({'error': 'Invalid path'}), 400
        
        # Normalize the path
        path = os.path.normpath(path)
        if not os.path.exists(path):
            return jsonify({'error': 'Path does not exist'}), 404
        
        if not os.path.isdir(path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        folders = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # Check if this directory has QFIL structure
                    qfil_path = os.path.join(item_path, QFIL_SUBDIR)
                    has_qfil_structure = os.path.exists(qfil_path) and os.path.isdir(qfil_path)
                    
                    folders.append({
                        'name': item,
                        'path': item_path,
                        'has_qfil_structure': has_qfil_structure
                    })
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Sort folders - QFIL folders first, then alphabetically
        folders.sort(key=lambda x: (not x['has_qfil_structure'], x['name'].lower()))
        
        return jsonify({
            'success': True,
            'current_path': path,
            'folders': folders
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_zip_with_progress(qfil_path, zip_path, download_id):
    """Create ZIP file with progress tracking"""
    try:
        # Get total file count for progress calculation
        all_files = []
        for root, dirs, files in os.walk(qfil_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        total_files = len(all_files)
        
        with download_lock:
            download_progress[download_id] = {
                'progress': 0,
                'status': 'starting',
                'total_files': total_files,
                'current_file': 0
            }
        
        # Create ZIP file with progress updates
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(all_files):
                # Create relative path within zip
                arcname = os.path.relpath(file_path, qfil_path)
                zipf.write(file_path, arcname)
                
                # Update progress
                progress = int((i + 1) / total_files * 100)
                with download_lock:
                    download_progress[download_id] = {
                        'progress': progress,
                        'status': 'zipping',
                        'total_files': total_files,
                        'current_file': i + 1,
                        'current_filename': os.path.basename(file_path)
                    }
        
        # Mark as complete
        with download_lock:
            download_progress[download_id]['status'] = 'complete'
            download_progress[download_id]['progress'] = 100
        
        return True
        
    except Exception as e:
        with download_lock:
            download_progress[download_id] = {
                'progress': 0,
                'status': 'error',
                'error': str(e)
            }
        return False

@app.route('/download/<path:project_name>')
def download_qfil(project_name):
    """Download QFIL package for specified project"""
    
    # Validate project name (security check) - allow URL-safe characters
    if not project_name or len(project_name) > 100:
        abort(400, 'Invalid project name length')
    
    # Check for path traversal patterns (but allow URL-encoded characters)
    if '..' in project_name:
        abort(400, 'Invalid project name format')
    
    # Find project in manual list
    projects = load_projects()
    project_config = next((p for p in projects if p['name'] == project_name), None)
    
    if not project_config:
        abort(404, f'Project not found: {project_name}')
    
    project_path = Path(project_config['path'])
    qfil_path = project_path / QFIL_SUBDIR
    
    if not qfil_path.exists():
        abort(404, f'QFIL package not found for project: {project_name}')
    
    # Generate unique download ID
    download_id = f"{project_name}_{int(time.time())}"
    
    # Create temporary directory for zip file
    temp_dir = tempfile.mkdtemp(prefix='qfil_download_')
    zip_filename = f'{project_name}_qfil_package.zip'
    zip_path = os.path.join(temp_dir, zip_filename)
    
    # Check if this is a progress request
    if request.args.get('progress') == 'true':
        return jsonify({'download_id': download_id})
    
    try:
        # Create ZIP file with progress tracking
        success = create_zip_with_progress(qfil_path, zip_path, download_id)
        
        if not success:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            abort(500, 'Error creating download package')
        
        # Clean up progress tracking after a delay
        def cleanup_progress():
            time.sleep(300)  # 5 minutes
            with download_lock:
                download_progress.pop(download_id, None)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        cleanup_thread = threading.Thread(target=cleanup_progress)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
    
    except Exception as e:
        # Cleanup on error
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        with download_lock:
            download_progress.pop(download_id, None)
        abort(500, f'Error creating download package: {str(e)}')

@app.route('/project/<path:project_name>')
def project_details(project_name):
    """Show details for a specific project"""
    
    # Validate project name (security check)
    if not project_name or len(project_name) > 100:
        abort(400, 'Invalid project name length')
    
    # Check for path traversal patterns (but allow URL-encoded characters)
    if '..' in project_name:
        abort(400, 'Invalid project name format')
    
    # Find project in manual list
    projects = load_projects()
    project_config = next((p for p in projects if p['name'] == project_name), None)
    
    if not project_config:
        abort(404, f'Project not found: {project_name}')
    
    project_path = Path(project_config['path'])
    qfil_path = project_path / QFIL_SUBDIR
    
    if not qfil_path.exists():
        abort(404, f'QFIL package not found for project: {project_name}')
    
    # Get file listing
    files = []
    try:
        for item in qfil_path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(qfil_path)
                files.append({
                    'name': item.name,
                    'path': str(rel_path),
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime)
                })
    except (OSError, IOError):
        pass
    
    files.sort(key=lambda x: x['name'])
    
    project_info = {
        'name': project_name,
        'files': files,
        'total_files': len(files),
        'total_size': sum(f['size'] for f in files),
        'description': project_config.get('description', ''),
        'path': project_config['path']
    }
    
    return render_template('project_details.html', project=project_info, format_size=format_file_size)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page not found', message=str(error.description)), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error', message=str(error.description)), 500

if __name__ == '__main__':
    # Note: Projects are manually added via the web interface
    print("QFIL Downloader Server Starting...")
    print(f"Projects are managed manually via the web interface")
    print(f"Looking for QFIL structure: <project_path>/{QFIL_SUBDIR}/")
    
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Run the application
    app.run(host=host, port=port, debug=debug)