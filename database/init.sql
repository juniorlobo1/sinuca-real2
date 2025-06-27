-- Inicialização do banco de dados Sinuca Real
-- Este arquivo será executado automaticamente pelo Railway

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Inserir dados iniciais de exemplo
INSERT INTO users (email, name, password_hash, balance, skill_rating) VALUES
('joao@exemplo.com', 'João Silva', 'hash_senha_joao', 100.00, 1380),
('maria@exemplo.com', 'Maria Costa', 'hash_senha_maria', 150.00, 1520),
('carlos@exemplo.com', 'Carlos Lima', 'hash_senha_carlos', 75.00, 1200)
ON CONFLICT (email) DO NOTHING;

-- Inserir apostas de exemplo
INSERT INTO bets (creator_id, amount, platform_fee, total_prize, status) VALUES
(1, 25.00, 2.50, 47.50, 'open'),
(2, 50.00, 5.00, 95.00, 'open'),
(3, 10.00, 1.00, 19.00, 'open')
ON CONFLICT DO NOTHING;

-- Inserir estatísticas iniciais
INSERT INTO platform_stats (date, total_bets, total_volume, platform_revenue, active_users) VALUES
(CURRENT_DATE, 0, 0.00, 0.00, 0)
ON CONFLICT (date) DO NOTHING;

