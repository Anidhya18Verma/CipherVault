from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def token_required(f):
    """Decorator: require valid JWT (from Authorization header or cookie)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: require valid JWT AND admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_admin:
                return jsonify({'error': 'Forbidden', 'message': 'Admin access required'}), 403
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Get the current authenticated user object."""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except Exception:
        return None
