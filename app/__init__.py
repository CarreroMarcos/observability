def create_app():
    from flask import Flask, g, request, current_app
    from app.routes import routes_bp
    import uuid
    import logging
    import time
    import traceback
    from app.metrics import http_requests_total, request_latency_seconds

    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            from flask import g
            record.request_id = getattr(g, 'request_id', 'no-request-id')
            return True

    app = Flask(__name__)
    app.register_blueprint(routes_bp)

    @app.errorhandler(Exception)
    def handle_exception(e):
        current_app.logger.error("Unhandled exception", extra={
            "error_details": str(e),
            "traceback": traceback.format_exc()
        })
        g.is_error = True
        http_requests_total.labels(method=request.method, endpoint=request.path, status_code="500").inc()
        return {"error": "Internal Server Error", "request_id": getattr(g, 'request_id', 'no-request-id')}, 500

    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

    @app.after_request
    def inject_request_id(response):
        response.headers['X-Request-ID'] = g.request_id
        # Record metrics
        duration = time.time() - g.start_time
        method = request.method
        endpoint = request.path
        status_code = response.status_code
        if not getattr(g, 'is_error', False):
            http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        request_latency_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        return response

    from pythonjsonlogger import jsonlogger as _jsonlogger
    handler = app.logger.handlers[0]
    formatter = _jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(message)s %(request_id)s',
        rename_fields={'levelname': 'level', 'asctime': 'timestamp'}
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())
    app.logger.setLevel("INFO")
    
    return app