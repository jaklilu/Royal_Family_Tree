from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
import logging
from config import Config
from models import db

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # CORS configuration
    CORS(app, origins=Config.ALLOWED_ORIGINS, supports_credentials=False)
    
    # Register blueprints
    from routes import api_bp, admin_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        logger.info(f'{request.method} {request.path}')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': {'code': 'NOT_FOUND', 'message': 'Resource not found'}}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal error: {error}', exc_info=True)
        return {'error': {'code': 'SERVER_ERROR', 'message': 'Internal server error'}}, 500
    
    # Cache headers for read-only API
    @app.after_request
    def add_cache_headers(response):
        if request.path.startswith('/api/'):
            response.cache_control.max_age = 300  # 5 minutes
        return response
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

