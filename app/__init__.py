from flask import Flask, render_template, session, redirect, url_for, request, Response, jsonify
from time import sleep
import os
from pathlib import Path
from math import ceil
from app.decorators import redirect_login_required, admin_required
from app.reports.models import Report
from mongoengine import connect
from app.user.forms import RegisterForm

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        MONGODB_URL = "mongodb://127.0.0.1:27017/test",
        UPLOAD_FOLDER = "app/static/imgs/uploads",
        ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'},
        MAX_CONTENT_LENGTH = 16_000_000,
        CREATE_TEST_ADMIN = True,
        COORDENADAS = 'coordenadas.csv',
        YOLO_WEIGHTS = '',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    for file in [app.config['UPLOAD_FOLDER'], app.config['COORDENADAS']]:
        if not os.path.exists(file):
            try:
                Path(file).touch()
            except OSError:
                print(f"Directory or file {file} doesn't exist and cannot be created")
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from app.user import create_module as create_module_user
    from app.reports import create_module as create_module_reports
    from app.inference import create_module as create_module_inference

    connect(host=app.config['MONGODB_URL'])
    create_module_user(app)
    create_module_reports(app)
    create_module_inference(app)

    @app.route("/")
    def root() :
        if 'logged_in' in session:
            return redirect(url_for('home'))
        else:
            return redirect(url_for("user.signin"))
           
    @app.route('/home/')
    @redirect_login_required
    def home():
        return render_template('home.html', page_name="Monitor - CV SECURITY", navclass={'home': 'active'})

    @app.route('/camera/')
    @redirect_login_required
    def camera():
        edit = session['user']['is_admin']
        return render_template('camera.html', page_name="Câmera - CV SECURITY", navclass={'camera': 'active'}, edit=edit)

    @app.route('/relatorios/')
    @redirect_login_required
    def relatorios():
        per_page = 10
        page = int(request.args.get('page', '1'))
        page = 1 if page == 0 else page
        total_pages = max(1, ceil(Report.objects.count() / per_page))
        page = total_pages if page > total_pages else page

        reports = Report.objects().order_by("-date").skip(per_page*(page-1)).limit(per_page)
        locals = [report.location for report in reports]
        images = [report.image_url for report in reports]
        dates = [report.date.isoformat() for report in reports]
        n_rows = len(locals)
        
        if total_pages >= 1:
            pages = []
            if total_pages <= 3:
                pages = list(range(1, total_pages + 1))
            elif page == 1:
                pages = [1, 2, 3]
            elif page == total_pages:
                pages = [page - 2, page - 1, page]
            else:
                pages = [page - 1, page, page + 1]
        else:
            pages = []

        return render_template('relatorios.html', page_name="Relatórios - CV SECURITY",
                               navclass={'relatorios': 'active'},
                               locals=locals,
                               images=images,
                               n_rows=n_rows,
                               dates=dates,
                               current_page=page,
                               pages=pages,
                               n_indexes=len(pages),
                               total_pages=total_pages)
    
    return app