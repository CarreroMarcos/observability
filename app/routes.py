from flask import Blueprint, current_app, g, Response, request
from app.database import check_db_connection
from prometheus_client import generate_latest
import os
import time

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/health', methods=['GET'])
def health_check():
    if not check_db_connection():
        current_app.logger.error("Health check failed")
        return {"status": "unhealthy"}, 503

    current_app.logger.info("Health check passed")
    return {"status": "healthy"}, 200

@routes_bp.route('/metrics', methods=['GET'])
def metrics():
    current_app.logger.info("Metrics requested")
    return Response(generate_latest(), mimetype='text/plain; charset=utf-8')

@routes_bp.route('/login', methods=['POST'])
def login():
    try:
        CHAOS_MODE = os.environ.get('CHAOS_MODE')
        if CHAOS_MODE == "True":
            time.sleep(2)
            raise Exception("Chaos!")
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == 'admin' and password == 'password':
            current_app.logger.info("Login successful")
            return {"message": "Login successful"}, 200
        else:
            current_app.logger.warning("Login failed")
            return {"message": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Exception in login", extra={"error": str(e)})
        raise  # Re-raise to let the global error handler deal with it
