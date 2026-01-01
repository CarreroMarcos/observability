from flask import Blueprint, current_app, g, Response
from app.database import check_db_connection
from prometheus_client import generate_latest

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