from flask import Flask
from flask_login import LoginManager
from config import config
from models import db, User
from utils.decorators import login_manager


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp
    from routes.faculty import faculty_bp
    from routes.common import common_bp
    from routes.security import security_bp
    from routes.api.chat import chat_api_bp
    from routes.api.face import face_api_bp
    from routes.api.voice import voice_api_bp
    from routes.api.emotion import emotion_api_bp
    from routes.api.anonymous import anonymous_api_bp
    from routes.api.visitor import visitor_api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(security_bp, url_prefix='/security')
    app.register_blueprint(common_bp)
    app.register_blueprint(chat_api_bp, url_prefix='/api/chat')
    app.register_blueprint(face_api_bp, url_prefix='/api/face')
    app.register_blueprint(voice_api_bp, url_prefix='/api/voice')
    app.register_blueprint(emotion_api_bp, url_prefix='/api/emotion')
    app.register_blueprint(anonymous_api_bp, url_prefix='/api/anonymous')
    app.register_blueprint(visitor_api_bp, url_prefix='/api/visitor')
    
    from routes.counselor import counselor_bp
    app.register_blueprint(counselor_bp, url_prefix='/counselor')
    
    from routes.visitor_entry import visitor_entry_bp
    app.register_blueprint(visitor_entry_bp, url_prefix='/visitor-entry')
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return "Access Forbidden", 403
    
    @app.errorhandler(404)
    def not_found(e):
        return "Page Not Found", 404
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return "Internal Server Error", 500
    
    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Initialize chatbot with API key
        import os
        from services.chatbot import chatbot
        api_key = os.environ.get('GOOGLE_API_KEY')
        if api_key:
            chatbot.initialize(api_key)
            print("Chatbot initialized successfully with Google API key")
        else:
            print("Warning: GOOGLE_API_KEY not found. Chatbot will not work.")
        
        # Load face encodings for recognition
        from services.face_recognition import face_recognition_service
        face_recognition_service.load_known_faces()
        
        # Load visitor faces for returning visitor recognition
        from services.visitor_service import visitor_service
        visitor_service.load_visitor_faces()
        print("Visitor service initialized")
        
        # Initialize emotion detection service
        from services.emotion_detection import emotion_service
        emotion_service.initialize()
        print("Emotion detection service initialized")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
