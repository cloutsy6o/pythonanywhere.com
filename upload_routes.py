from flask import Blueprint, send_from_directory, current_app
import os

upload_bp = Blueprint('upload', __name__, url_prefix='/uploads')

# Ensure upload directory exists on startup
UPLOAD_BASE = 'uploads'
if not os.path.exists(UPLOAD_BASE):
    os.makedirs(UPLOAD_BASE)
    os.makedirs(os.path.join(UPLOAD_BASE, 'tickets'))
    print(f"✅ Created upload directory: {UPLOAD_BASE}/")

@upload_bp.route('/<path:filename>')
def serve_file(filename):
    """Serve uploaded files securely"""
    try:
        # Security: Only serve files from allowed directories
        if not filename.startswith('tickets/'):
            return "Zugriff verweigert", 403

        # Sanitize filename path
        safe_path = os.path.normpath(filename).lstrip('/')
        if '..' in safe_path or safe_path.startswith('/'):
            return "Ungültiger Dateipfad", 400

        # Serve file
        return send_from_directory(UPLOAD_BASE, safe_path)
    except Exception as e:
        current_app.logger.error(f"File serve error: {str(e)}")
        return "Datei nicht gefunden", 404

# Optional: Add route to check upload directory
@upload_bp.route('/health')
def upload_health():
    """Check if upload directory is accessible"""
    try:
        stats = {
            'upload_dir_exists': os.path.exists(UPLOAD_BASE),
            'tickets_dir_exists': os.path.exists(os.path.join(UPLOAD_BASE, 'tickets')),
            'total_size': 0
        }

        # Calculate total size of uploads
        if stats['upload_dir_exists']:
            for root, dirs, files in os.walk(UPLOAD_BASE):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        stats['total_size'] += os.path.getsize(filepath)
                    except:
                        pass

        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        return stats
    except Exception as e:
        return {'error': str(e)}, 500
