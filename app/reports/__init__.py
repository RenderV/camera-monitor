def create_module(app):
    from .views import report_bp
    app.register_blueprint(report_bp, url_prefix="/report/")