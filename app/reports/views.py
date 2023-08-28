from flask import jsonify, Blueprint, request, Response, current_app
from time import sleep
from mongoengine import *
from app.reports.models import Report
from datetime import datetime
from app.decorators import api_login_required
from werkzeug.utils import secure_filename
import os, hashlib

report_bp = Blueprint('report', __name__, url_prefix='/report/')

def jsonify_query(q):
    return jsonify([i.asdict() for i in q])

def filter_by_location(query, args):
    valor = args.get('valor')
    if valor:
        return query(location=valor)
    else:
        return query()

def filter_by_image_url(query, args):
    valor = args.get('valor')
    if valor:
        return query(image_url=valor)
    else:
        return query()

def filter_by_date(query, args):
    time_format = "%d-%m-%Y-%H:%M"
    valor = args.get('valor')
    ate = args.get('ate', datetime.strftime(datetime.utcnow(), time_format))
    ate = datetime.strptime(ate, time_format)
    de = args.get('de', "01-01-2000-00:00")
    de = datetime.strptime(de, time_format)
    if valor:
        valor = datetime.strptime(valor, time_format)
        return query(date=valor)
    else:
        return query(date__gte=de, date__lte=ate)

@report_bp.route("/search", methods=["GET"])
@api_login_required
def get_reports():
    quantidade = min(int(request.args.get('quantidade', 20)), 20)

    filters = {
        'location': filter_by_location,
        'image_url': filter_by_image_url,
        'date': filter_by_date,
    }

    por = request.args.get('por')

    query = Report.objects
    
    try:
        response = filters[por](query, request.args).limit(quantidade)
    except ValueError:
        return jsonify({'error': 'Valores invalidos'}), 400

    return jsonify_query(response), 200

@report_bp.route("/get_count")
@api_login_required
def get_count():
    q = Report.objects
    try:
        count = filter_by_date(q, request.args).count()
        return jsonify({'total': count}), 200
    except ValueError as e:
        return jsonify({'error': 'Valores Invalidos'}), 400
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@report_bp.route('/add', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        resp = jsonify({'message' : 'Nenhum arquivo foi adicionado no corpo da requisição.'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'Nenhum arquivo foi selecionado para upload'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
        extension = '.'+filename.split('.')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_hash+extension)

        report = Report(
            location = request.form.get('location'),
            image_url = file_hash+extension
        )
        try:
            report.validate()
        except ValidationError as e:
            return jsonify({"error": "Dados faltantes ou invalidos"}), 400
        try:
            report.save()
        except NotUniqueError:
            return jsonify({"error": "Imagem já existe na base de dados"}), 400

        file.save(file_path)

        return jsonify({'message' : 'Arquivo enviado com sucesso'}), 201
    else:
        return jsonify({'message' : 'Tipos de arquivo permitidos são PNG e JPG'}), 400

@report_bp.route('/remove_by_img', methods=['DELETE'])
@api_login_required
def remove_by_img():
    image_url = request.args.get('image_url')
    r = Report.objects(image_url=image_url)
    if r:
        r.first().delete()
        try:
            os.remove(image_url)
        except FileNotFoundError:
            pass
        return jsonify({'message': 'Imagem deletada com sucesso'}), 200
    return jsonify({'error': 'Registro não encontrado'}), 400

@report_bp.route('/del_all', methods=['DELETE'])
@api_login_required
def del_all():
    Report.objects.delete()
    for file in os.listdir(current_app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file))
    return jsonify({'message': 'Tudo foi deletado'}), 200
    

@report_bp.route('/stream')
@api_login_required
def stream():
    def generate():
        last_report = None
        while True:
            q = Report.objects.order_by('-id').first()
            if ((last_report is None) or q!=last_report) and q is not None:
                last_report = q
                yield  f"data: {q.json()}\n\n"
            sleep(100)
    return Response(generate(), mimetype='text/event-stream')