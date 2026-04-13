from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import User, Note
from app.services import encrypt_note, decrypt_note
from app.utils import token_required, admin_required, get_current_user

main = Blueprint('main', __name__)

# ─────────────────────────────────────────────
# PUBLIC WEB PAGES
# ─────────────────────────────────────────────

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/features')
def features():
    return render_template('features.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')


# ─────────────────────────────────────────────
# AUTH WEB PAGES
# ─────────────────────────────────────────────

@main.route('/login')
def login_page():
    return render_template('login.html')

@main.route('/register')
def register_page():
    return render_template('register.html')


# ─────────────────────────────────────────────
# PROTECTED WEB PAGES
# ─────────────────────────────────────────────

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/admin-panel')
def admin_panel():
    return render_template('admin_panel.html')


# ─────────────────────────────────────────────
# REST API – AUTH
# ─────────────────────────────────────────────

@main.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required'}), 400

    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


@main.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


@main.route('/api/auth/me', methods=['GET'])
@token_required
def api_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


# ─────────────────────────────────────────────
# REST API – NOTES (VAULT)
# ─────────────────────────────────────────────

@main.route('/api/notes', methods=['GET'])
@token_required
def api_get_notes():
    user_id = int(get_jwt_identity())
    favorite_only = request.args.get('favorites', 'false').lower() == 'true'

    query = Note.query.filter_by(user_id=user_id)
    if favorite_only:
        query = query.filter_by(is_favorite=True)

    notes = query.order_by(Note.created_at.desc()).all()
    result = []
    for note in notes:
        decrypted = decrypt_note(note.encrypted_content)
        d = note.to_dict(decrypted_content=decrypted)
        d['encrypted_content'] = note.encrypted_content
        result.append(d)

    return jsonify({'notes': result}), 200


@main.route('/api/notes', methods=['POST'])
@token_required
def api_create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    encrypted = encrypt_note(content)
    note = Note(
        user_id=user_id,
        title=title,
        encrypted_content=encrypted,
        is_favorite=data.get('is_favorite', False)
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({
        'message': 'Note created successfully',
        'note': note.to_dict(decrypted_content=content)
    }), 201


@main.route('/api/notes/<int:note_id>', methods=['DELETE'])
@token_required
def api_delete_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted successfully'}), 200


@main.route('/api/notes/<int:note_id>/favorite', methods=['PATCH'])
@token_required
def api_toggle_favorite(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    note.is_favorite = not note.is_favorite
    db.session.commit()
    return jsonify({
        'message': 'Favorite updated',
        'is_favorite': note.is_favorite
    }), 200


# ─────────────────────────────────────────────
# REST API – ADMIN
# ─────────────────────────────────────────────

@main.route('/api/admin/users', methods=['GET'])
@admin_required
def api_admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@main.route('/api/admin/notes', methods=['GET'])
@admin_required
def api_admin_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    result = []
    for note in notes:
        d = note.to_dict()
        owner = User.query.get(note.user_id)
        d['owner_username'] = owner.username if owner else 'unknown'
        result.append(d)
    return jsonify({'notes': result}), 200


@main.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.is_admin:
        return jsonify({'error': 'Cannot delete admin user'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200
