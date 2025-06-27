import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuração para Railway
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Configuração CORS para Railway
CORS(app, origins=["*"])

# Configuração do banco de dados para Railway
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///sinucareal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar banco
db = SQLAlchemy(app)

# Modelos do banco de dados
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    total_winnings = db.Column(db.Numeric(10, 2), default=0.00)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    skill_rating = db.Column(db.Integer, default=1200)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Bet(db.Model):
    __tablename__ = 'bets'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    opponent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_prize = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='open')
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Criar tabelas
with app.app_context():
    db.create_all()
    
    # Inserir dados de exemplo se não existirem
    if User.query.count() == 0:
        users = [
            User(email='joao@exemplo.com', name='João Silva', password_hash='hash123', balance=100.00, skill_rating=1380),
            User(email='maria@exemplo.com', name='Maria Costa', password_hash='hash456', balance=150.00, skill_rating=1520),
            User(email='carlos@exemplo.com', name='Carlos Lima', password_hash='hash789', balance=75.00, skill_rating=1200)
        ]
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        # Adicionar apostas de exemplo
        bets = [
            Bet(creator_id=1, amount=25.00, platform_fee=2.50, total_prize=47.50, status='open'),
            Bet(creator_id=2, amount=50.00, platform_fee=5.00, total_prize=95.00, status='open'),
            Bet(creator_id=3, amount=10.00, platform_fee=1.00, total_prize=19.00, status='open')
        ]
        for bet in bets:
            db.session.add(bet)
        
        db.session.commit()

# Rotas da API
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Sinuca Real API',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    return health_check()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_users = User.query.count()
        total_bets = Bet.query.count()
        total_volume = db.session.query(db.func.sum(Bet.amount * 2)).scalar() or 0
        platform_revenue = db.session.query(db.func.sum(Bet.platform_fee)).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'total_bets': total_bets,
            'total_volume': float(total_volume),
            'platform_revenue': float(platform_revenue)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Verificar se usuário já existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar novo usuário
        user = User(
            email=data['email'],
            name=data['name'],
            password_hash=data['password'],
            balance=data.get('balance', 0)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'balance': float(user.balance)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bets', methods=['GET'])
def get_bets():
    try:
        bets = Bet.query.filter_by(status='open').all()
        return jsonify([{
            'id': bet.id,
            'creator_id': bet.creator_id,
            'amount': float(bet.amount),
            'platform_fee': float(bet.platform_fee),
            'total_prize': float(bet.total_prize),
            'created_at': bet.created_at.isoformat()
        } for bet in bets])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bets', methods=['POST'])
def create_bet():
    try:
        data = request.get_json()
        
        amount = float(data['amount'])
        platform_fee = amount * 0.05  # 5% de taxa
        total_prize = (amount * 2) - platform_fee
        
        bet = Bet(
            creator_id=data['creator_id'],
            amount=amount,
            platform_fee=platform_fee,
            total_prize=total_prize
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({
            'id': bet.id,
            'amount': float(bet.amount),
            'platform_fee': float(bet.platform_fee),
            'total_prize': float(bet.total_prize)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Para Railway
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
