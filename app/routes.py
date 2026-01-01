from flask import Blueprint
from app.database import check_db_connection

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/health', methods=['GET'])
def health_check():
    if not check_db_connection():
        return {"status": "unhealthy"}, 503

    return {"status": "healthy"}, 200