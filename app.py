from flask import Flask, request, g, abort, Response, jsonify
from flask_migrate import  Migrate
from flask_httpauth import HTTPBasicAuth
from models import db, User, Advertisement
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:1234@localhost:5431/mydb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:1234@localhost:5431/mydb"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # регистрируйте маршруты, auth, ошибки и т.д.

    return app

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.set_password(password):
        g.current_user = user
        return True
    return False

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "User created"}), 201

@app.route('/ads', methods=['POST'])
@auth.login_required
def create_ad():
    data = request.get_json()
    if not data or not data['title']:
        return jsonify({"error": "Title is required"}), 400

    ad = Advertisement(
        title = data['title'],
        description = data.get('description', ''),
        owner_id = g.current_user.id
    )

    db.session.add(ad)
    db.session.commit()
    return jsonify({
        'id': ad.id,
        'title': ad.title,
        'description': ad.description,
        'created_ad': ad.created_at.isoformat(),
        'owner_id': ad.owner_id
    })

@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    base = {
        'id': ad.id,
        'title': ad.title,
        'description': ad.description,
        'created_ad': ad.created_at.isoformat(),
        'owner_id': ad.owner_id
    }

    return Response(json.dumps(base, indent=2, ensure_ascii=False))

@app.route('/ads/<int:ad_id>', methods=['DELETE'])
@auth.login_required
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.owner_id != g.current_user.id:
        abort(403, advertisement="U no have auth delete this ad")

    db.session.delete(ad)
    db.session.commit()
    return '', 204

@app.route('/ads/<int:ad_id>', methods=['PUT'])
def edit_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    if ad.owner_id != g.current_user.id:
        abort(403, advertisement="U no have auth edit this ad")

    data = request.get_json()
    ad.title = data.get('title', ad.title)
    ad.description = data.get('description', ad.description)
    db.session.commit()
    return '', 204