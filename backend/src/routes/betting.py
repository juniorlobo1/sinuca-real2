from flask import Blueprint, request, jsonify
from src.models.betting import db, User, Bet, Transaction, EscrowAccount, PlatformRevenue
from decimal import Decimal
from datetime import datetime
import json

betting_bp = Blueprint('betting', __name__)

@betting_bp.route('/users', methods=['POST'])
def create_user():
    """Criar novo usuário"""
    try:
        data = request.get_json()
        
        # Verificar se usuário já existe
        existing_user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Usuário ou email já existe'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],  # Em produção, usar hash seguro
            wallet_balance=data.get('initial_balance', 0.00)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/users/<user_id>/wallet', methods=['GET'])
def get_wallet_balance(user_id):
    """Obter saldo da carteira do usuário"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'wallet_balance': float(user.wallet_balance),
            'total_earnings': float(user.total_earnings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/users/<user_id>/deposit', methods=['POST'])
def deposit_funds(user_id):
    """Depositar fundos na carteira do usuário"""
    try:
        data = request.get_json()
        amount = Decimal(str(data['amount']))
        payment_method = data.get('payment_method', 'pix')
        
        if amount <= 0:
            return jsonify({'error': 'Valor deve ser maior que zero'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Criar transação de depósito
        transaction = Transaction(
            user_id=user.id,
            type='deposit',
            amount=amount,
            payment_method=payment_method,
            status='completed',  # Em produção, seria 'pending' até confirmação do pagamento
            description=f'Depósito via {payment_method}',
            processed_at=datetime.utcnow()
        )
        
        # Atualizar saldo do usuário
        user.wallet_balance += amount
        user.updated_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Depósito realizado com sucesso',
            'transaction': transaction.to_dict(),
            'new_balance': float(user.wallet_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/bets', methods=['POST'])
def create_bet():
    """Criar nova aposta"""
    try:
        data = request.get_json()
        player1_id = data['player1_id']
        bet_amount = Decimal(str(data['bet_amount']))
        
        if bet_amount <= 0:
            return jsonify({'error': 'Valor da aposta deve ser maior que zero'}), 400
        
        player1 = User.query.get_or_404(player1_id)
        
        # Verificar se o jogador tem saldo suficiente
        if player1.wallet_balance < bet_amount:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Criar aposta
        bet = Bet(
            player1_id=player1_id,
            bet_amount=bet_amount
        )
        
        # Calcular taxas (assumindo que o oponente apostará o mesmo valor)
        bet.calculate_fees()
        
        db.session.add(bet)
        db.session.flush()  # Para obter o ID da aposta
        
        # Debitar valor da carteira do jogador 1
        player1.wallet_balance -= bet_amount
        
        # Criar transação de débito
        transaction = Transaction(
            user_id=player1_id,
            type='bet_debit',
            amount=-bet_amount,
            bet_id=bet.id,
            status='completed',
            description=f'Aposta criada - ID: {bet.id}',
            processed_at=datetime.utcnow()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Aposta criada com sucesso',
            'bet': bet.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/bets/<bet_id>/accept', methods=['POST'])
def accept_bet(bet_id):
    """Aceitar uma aposta existente"""
    try:
        data = request.get_json()
        player2_id = data['player2_id']
        
        bet = Bet.query.get_or_404(bet_id)
        
        if bet.status != 'pending':
            return jsonify({'error': 'Aposta não está disponível'}), 400
        
        if bet.player1_id == player2_id:
            return jsonify({'error': 'Não é possível apostar contra si mesmo'}), 400
        
        player2 = User.query.get_or_404(player2_id)
        
        # Verificar se o jogador 2 tem saldo suficiente
        if player2.wallet_balance < bet.bet_amount:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Atualizar aposta
        bet.player2_id = player2_id
        bet.status = 'active'
        bet.started_at = datetime.utcnow()
        
        # Debitar valor da carteira do jogador 2
        player2.wallet_balance -= bet.bet_amount
        
        # Criar transação de débito para jogador 2
        transaction = Transaction(
            user_id=player2_id,
            type='bet_debit',
            amount=-bet.bet_amount,
            bet_id=bet.id,
            status='completed',
            description=f'Aposta aceita - ID: {bet.id}',
            processed_at=datetime.utcnow()
        )
        
        # Criar conta de escrow
        escrow = EscrowAccount(
            bet_id=bet.id,
            player1_amount=bet.bet_amount,
            player2_amount=bet.bet_amount,
            platform_fee=bet.platform_fee,
            total_amount=bet.bet_amount * 2
        )
        
        db.session.add(transaction)
        db.session.add(escrow)
        db.session.commit()
        
        return jsonify({
            'message': 'Aposta aceita com sucesso',
            'bet': bet.to_dict(),
            'escrow': escrow.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/bets/<bet_id>/complete', methods=['POST'])
def complete_bet(bet_id):
    """Finalizar aposta com resultado"""
    try:
        data = request.get_json()
        winner_id = data['winner_id']
        game_data = data.get('game_data', {})
        
        bet = Bet.query.get_or_404(bet_id)
        
        if bet.status != 'active':
            return jsonify({'error': 'Aposta não está ativa'}), 400
        
        if winner_id not in [bet.player1_id, bet.player2_id]:
            return jsonify({'error': 'Vencedor inválido'}), 400
        
        winner = User.query.get_or_404(winner_id)
        loser_id = bet.player1_id if winner_id == bet.player2_id else bet.player2_id
        loser = User.query.get_or_404(loser_id)
        
        # Atualizar aposta
        bet.winner_id = winner_id
        bet.status = 'completed'
        bet.completed_at = datetime.utcnow()
        bet.game_data = json.dumps(game_data)
        
        # Liberar escrow
        escrow = EscrowAccount.query.filter_by(bet_id=bet.id).first()
        if escrow:
            escrow.status = 'released'
            escrow.released_at = datetime.utcnow()
        
        # Creditar prêmio para o vencedor
        winner.wallet_balance += bet.total_prize
        winner.games_won += 1
        winner.total_games += 1
        winner.total_earnings += bet.total_prize
        
        # Atualizar estatísticas do perdedor
        loser.total_games += 1
        
        # Atualizar ratings (sistema ELO simplificado)
        rating_change = 20  # Simplificado
        winner.skill_rating += rating_change
        loser.skill_rating -= rating_change
        
        # Criar transação de crédito para o vencedor
        win_transaction = Transaction(
            user_id=winner_id,
            type='bet_credit',
            amount=bet.total_prize,
            bet_id=bet.id,
            status='completed',
            description=f'Vitória na aposta - ID: {bet.id}',
            processed_at=datetime.utcnow()
        )
        
        # Registrar receita da plataforma
        platform_revenue = PlatformRevenue(
            bet_id=bet.id,
            amount=bet.platform_fee
        )
        
        db.session.add(win_transaction)
        db.session.add(platform_revenue)
        db.session.commit()
        
        return jsonify({
            'message': 'Aposta finalizada com sucesso',
            'bet': bet.to_dict(),
            'winner': winner.to_dict(),
            'platform_fee_collected': float(bet.platform_fee)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/bets/available', methods=['GET'])
def get_available_bets():
    """Listar apostas disponíveis"""
    try:
        user_id = request.args.get('user_id')
        min_amount = request.args.get('min_amount', 0)
        max_amount = request.args.get('max_amount', 999999)
        
        query = Bet.query.filter_by(status='pending')
        
        if user_id:
            query = query.filter(Bet.player1_id != user_id)
        
        query = query.filter(
            Bet.bet_amount >= Decimal(str(min_amount)),
            Bet.bet_amount <= Decimal(str(max_amount))
        )
        
        bets = query.order_by(Bet.created_at.desc()).limit(20).all()
        
        return jsonify({
            'available_bets': [bet.to_dict() for bet in bets]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/users/<user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    """Obter histórico de transações do usuário"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@betting_bp.route('/platform/revenue', methods=['GET'])
def get_platform_revenue():
    """Obter estatísticas de receita da plataforma"""
    try:
        # Receita total
        total_revenue = db.session.query(db.func.sum(PlatformRevenue.amount)).scalar() or 0
        
        # Receita hoje
        today = datetime.utcnow().date()
        today_revenue = db.session.query(db.func.sum(PlatformRevenue.amount))\
            .filter(db.func.date(PlatformRevenue.date_collected) == today).scalar() or 0
        
        # Total de apostas processadas
        total_bets = Bet.query.filter_by(status='completed').count()
        
        # Volume total apostado
        total_volume = db.session.query(db.func.sum(Bet.bet_amount * 2))\
            .filter_by(status='completed').scalar() or 0
        
        return jsonify({
            'total_revenue': float(total_revenue),
            'today_revenue': float(today_revenue),
            'total_bets_completed': total_bets,
            'total_volume': float(total_volume),
            'average_fee_per_bet': float(total_revenue / total_bets) if total_bets > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

