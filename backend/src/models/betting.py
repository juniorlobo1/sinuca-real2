from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from decimal import Decimal

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    wallet_balance = db.Column(db.Numeric(10, 2), default=0.00)
    skill_rating = db.Column(db.Integer, default=1000)
    total_games = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    bets_as_player1 = db.relationship('Bet', foreign_keys='Bet.player1_id', backref='player1')
    bets_as_player2 = db.relationship('Bet', foreign_keys='Bet.player2_id', backref='player2')
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'wallet_balance': float(self.wallet_balance),
            'skill_rating': self.skill_rating,
            'total_games': self.total_games,
            'games_won': self.games_won,
            'win_rate': (self.games_won / self.total_games * 100) if self.total_games > 0 else 0,
            'total_earnings': float(self.total_earnings),
            'created_at': self.created_at.isoformat()
        }

class Bet(db.Model):
    __tablename__ = 'bets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player1_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    bet_amount = db.Column(db.Numeric(10, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_prize = db.Column(db.Numeric(10, 2), nullable=False)
    winner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    game_data = db.Column(db.Text)  # JSON com dados da partida
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relacionamentos
    winner = db.relationship('User', foreign_keys=[winner_id])
    transactions = db.relationship('Transaction', backref='bet', lazy=True)
    
    def calculate_fees(self):
        """Calcula a taxa de 5% sobre o valor total apostado"""
        total_bet = self.bet_amount * 2  # Assumindo que ambos jogadores apostam o mesmo valor
        self.platform_fee = total_bet * Decimal('0.05')
        self.total_prize = total_bet - self.platform_fee
        
    def to_dict(self):
        return {
            'id': self.id,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'bet_amount': float(self.bet_amount),
            'platform_fee': float(self.platform_fee),
            'total_prize': float(self.total_prize),
            'winner_id': self.winner_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, bet_debit, bet_credit, platform_fee
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    bet_id = db.Column(db.String(36), db.ForeignKey('bets.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    payment_method = db.Column(db.String(50))  # pix, credit_card, debit_card, wallet
    external_transaction_id = db.Column(db.String(255))  # ID da transação no gateway de pagamento
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': float(self.amount),
            'bet_id': self.bet_id,
            'status': self.status,
            'payment_method': self.payment_method,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class EscrowAccount(db.Model):
    __tablename__ = 'escrow_accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bet_id = db.Column(db.String(36), db.ForeignKey('bets.id'), nullable=False, unique=True)
    player1_amount = db.Column(db.Numeric(10, 2), nullable=False)
    player2_amount = db.Column(db.Numeric(10, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='holding')  # holding, released, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    
    # Relacionamento
    bet = db.relationship('Bet', backref=db.backref('escrow_account', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'bet_id': self.bet_id,
            'player1_amount': float(self.player1_amount),
            'player2_amount': float(self.player2_amount),
            'platform_fee': float(self.platform_fee),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'released_at': self.released_at.isoformat() if self.released_at else None
        }

class PlatformRevenue(db.Model):
    __tablename__ = 'platform_revenue'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bet_id = db.Column(db.String(36), db.ForeignKey('bets.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    percentage = db.Column(db.Numeric(5, 2), default=5.00)  # 5%
    date_collected = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    bet = db.relationship('Bet', backref='platform_revenue')
    
    def to_dict(self):
        return {
            'id': self.id,
            'bet_id': self.bet_id,
            'amount': float(self.amount),
            'percentage': float(self.percentage),
            'date_collected': self.date_collected.isoformat()
        }

