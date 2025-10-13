from flask import Flask, request, abort, g, Response, jsonify
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from models import db, User, Advertisement
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://user:1234@localhost:5431/mydb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        g.current_user = user
        return True
    return False

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "Create ok"}), 201

@app.route('/ads', methods=['POST'])
@auth.login_required
def created_ad():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({"error": "title is required"}), 400

    ad = Advertisement(
        title = data['title'],
        description = data.get('description', ''),
        owner_id = g.current_user.id
    )

    db.session.add(ad)
    db.session.commit()
    return jsonify({
        'id': ad.id,
        'title': ad.titile,
        'description': ad.description,
        'created_ad': ad.created_ad.isoformat(),
        'owner_id': ad.owner_id
    }), 201

@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    data = {
        'id': ad.id,
        'title': ad.titile,
        'description': ad.description,
        'created_ad': ad.created_ad.isoformat(),
        'owner_id': ad.owner_id
    }

    return Response(json.dumps(data, ensure_ascii=False), mimetype='application/json')

@app.route('/ads/<int:ad_id>', methods=['DELETE'])
@auth.login_required
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.owner_id != g.current_user.id:
        abort(403, 'You have no auth delete this ad')

    db.session.delete(ad)
    db.session.commit()
    return jsonify({"status": "delete ad = OK"}), 204