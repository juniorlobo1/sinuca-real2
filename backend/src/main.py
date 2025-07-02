#!/usr/bin/env python3
"""
API Backend Completa - Sistema de Sinuca Real
Inclui todas as rotas necessárias para funcionamento completo
"""

import os
import hashlib
import jwt
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuração da aplicação
app = Flask(__name__)
CORS(app, origins=["*"])

# Configurações
SECRET_KEY = os.environ.get('SECRET_KEY', 'sinuca-real-secret-key-2024')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Simulação de banco de dados em memória (para desenvolvimento)
# Em produção, usar PostgreSQL com DATABASE_URL
users_db = {}
games_db = {}
rankings_db = []

# Utilitários
def hash_password(password):
    """Hash da senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verificar senha"""
    return hash_password(password) == hashed

def generate_token(user_id):
    """Gerar JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verificar JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

# ==================== ROTAS DE TESTE ====================

@app.route('/', methods=['GET'])
def home():
    """Rota principal"""
    return jsonify({
        'message': 'API Sinuca Real - Backend Funcionando!',
        'version': '1.0.0',
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """Rota de teste da API"""
    return jsonify({
        'message': 'API funcionando perfeitamente!',
        'database_connected': DATABASE_URL is not None,
        'routes_available': [
            '/api/auth/register',
            '/api/auth/login',
            '/api/games',
            '/api/ranking',
            '/api/profile'
        ]
    })

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Cadastro de usuário"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['nome_completo', 'nome_usuario', 'email', 'senha']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        email = data['email']
        nome_usuario = data['nome_usuario']
        
        # Verificar se usuário já existe
        if email in users_db:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        if any(user['nome_usuario'] == nome_usuario for user in users_db.values()):
            return jsonify({'error': 'Nome de usuário já existe'}), 400
        
        # Criar usuário
        user_id = len(users_db) + 1
        users_db[email] = {
            'id': user_id,
            'nome_completo': data['nome_completo'],
            'nome_usuario': nome_usuario,
            'email': email,
            'senha': hash_password(data['senha']),
            'created_at': datetime.utcnow().isoformat(),
            'games_played': 0,
            'games_won': 0,
            'total_score': 0
        }
        
        # Gerar token
        token = generate_token(user_id)
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso!',
            'token': token,
            'user': {
                'id': user_id,
                'nome_completo': data['nome_completo'],
                'nome_usuario': nome_usuario,
                'email': email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Verificar usuário
        user = users_db.get(email)
        if not user or not verify_password(senha, user['senha']):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Gerar token
        token = generate_token(user['id'])
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'token': token,
            'user': {
                'id': user['id'],
                'nome_completo': user['nome_completo'],
                'nome_usuario': user['nome_usuario'],
                'email': user['email']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE JOGOS ====================

@app.route('/api/games', methods=['GET'])
def get_games():
    """Listar jogos disponíveis"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Retornar jogos disponíveis
        available_games = [
            {
                'id': 1,
                'name': 'Sinuca Clássica',
                'description': 'Jogo tradicional de sinuca com 15 bolas',
                'max_players': 2,
                'difficulty': 'medium'
            },
            {
                'id': 2,
                'name': 'Sinuca Rápida',
                'description': 'Versão rápida com menos bolas',
                'max_players': 2,
                'difficulty': 'easy'
            }
        ]
        
        return jsonify({
            'games': available_games,
            'total': len(available_games)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/games', methods=['POST'])
def create_game():
    """Criar novo jogo"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        game_type = data.get('type', 'classic')
        
        # Criar jogo
        game_id = len(games_db) + 1
        games_db[game_id] = {
            'id': game_id,
            'type': game_type,
            'player_id': user_id,
            'status': 'waiting',
            'created_at': datetime.utcnow().isoformat(),
            'score': 0,
            'balls_potted': 0
        }
        
        return jsonify({
            'message': 'Jogo criado com sucesso!',
            'game': games_db[game_id]
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/games/<int:game_id>/finish', methods=['POST'])
def finish_game(game_id):
    """Finalizar jogo"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar se jogo existe
        game = games_db.get(game_id)
        if not game:
            return jsonify({'error': 'Jogo não encontrado'}), 404
        
        if game['player_id'] != user_id:
            return jsonify({'error': 'Não autorizado'}), 403
        
        data = request.get_json()
        score = data.get('score', 0)
        balls_potted = data.get('balls_potted', 0)
        won = data.get('won', False)
        
        # Atualizar jogo
        game['status'] = 'finished'
        game['score'] = score
        game['balls_potted'] = balls_potted
        game['won'] = won
        game['finished_at'] = datetime.utcnow().isoformat()
        
        # Atualizar estatísticas do usuário
        user_email = None
        for email, user in users_db.items():
            if user['id'] == user_id:
                user_email = email
                break
        
        if user_email:
            user = users_db[user_email]
            user['games_played'] += 1
            user['total_score'] += score
            if won:
                user['games_won'] += 1
        
        # Adicionar ao ranking
        rankings_db.append({
            'user_id': user_id,
            'game_id': game_id,
            'score': score,
            'balls_potted': balls_potted,
            'won': won,
            'date': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'message': 'Jogo finalizado com sucesso!',
            'game': game
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE RANKING ====================

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    """Obter ranking dos jogadores"""
    try:
        # Calcular ranking baseado nas estatísticas dos usuários
        ranking = []
        
        for email, user in users_db.items():
            if user['games_played'] > 0:
                win_rate = (user['games_won'] / user['games_played']) * 100
                avg_score = user['total_score'] / user['games_played']
                
                ranking.append({
                    'position': 0,  # Será calculado depois
                    'nome_usuario': user['nome_usuario'],
                    'games_played': user['games_played'],
                    'games_won': user['games_won'],
                    'win_rate': round(win_rate, 1),
                    'total_score': user['total_score'],
                    'avg_score': round(avg_score, 1)
                })
        
        # Ordenar por pontuação total (decrescente)
        ranking.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Adicionar posições
        for i, player in enumerate(ranking):
            player['position'] = i + 1
        
        return jsonify({
            'ranking': ranking[:10],  # Top 10
            'total_players': len(ranking)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE PERFIL ====================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Obter perfil do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Encontrar usuário
        user = None
        for email, u in users_db.items():
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Calcular estatísticas
        win_rate = 0
        avg_score = 0
        
        if user['games_played'] > 0:
            win_rate = (user['games_won'] / user['games_played']) * 100
            avg_score = user['total_score'] / user['games_played']
        
        profile = {
            'id': user['id'],
            'nome_completo': user['nome_completo'],
            'nome_usuario': user['nome_usuario'],
            'email': user['email'],
            'member_since': user['created_at'],
            'statistics': {
                'games_played': user['games_played'],
                'games_won': user['games_won'],
                'win_rate': round(win_rate, 1),
                'total_score': user['total_score'],
                'avg_score': round(avg_score, 1)
            }
        }
        
        return jsonify({'profile': profile})
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE SISTEMA ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde do sistema"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database_url_configured': DATABASE_URL is not None,
        'users_count': len(users_db),
        'games_count': len(games_db),
        'rankings_count': len(rankings_db)
    })

# ==================== CONFIGURAÇÃO DO SERVIDOR ====================

if __name__ == '__main__':
    print("🎱 Backend de Pagamentos Sinuca Real iniciado na porta 5001!")
    print(f"🔗 DATABASE_URL configurada: {DATABASE_URL is not None}")
    print(f"🚀 Servidor rodando em modo {'produção' if not app.debug else 'desenvolvimento'}")
    
    # Configurar porta
    port = int(os.environ.get('PORT', 5001))
    
    # Rodar servidor
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )

