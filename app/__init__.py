def create_app():
    from flask import Flask, g
    from app.routes import routes_bp
    import uuid

    app = Flask(__name__)
    app.register_blueprint(routes_bp)

    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())

    from pythonjsonlogger import jsonlogger as _jsonlogger
    handler = app.logger.handlers[0]
    formatter = _jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    app.logger.setLevel("INFO")
    
    return app