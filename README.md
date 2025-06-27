# 🎱 Sinuca Real - Deploy no Railway

Sistema completo de apostas para Sinuca Real com deploy automatizado no Railway.

## 🚀 Deploy Rápido (5 minutos)

### 1. Fork este repositório
Clique em "Fork" no GitHub para criar sua cópia.

### 2. Conectar ao Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu fork do `sinuca-real`

### 3. Configurar Serviços

#### Backend (API)
- **Pasta:** `backend/`
- **Comando de build:** Automático
- **Porta:** Automática ($PORT)

#### Frontend (Interface)
- **Pasta:** `frontend/`
- **Comando de build:** `pnpm run build`
- **Pasta de deploy:** `dist/`

#### Banco de Dados
- **Tipo:** PostgreSQL
- **Configuração:** Automática
- **Variável:** `DATABASE_URL`

### 4. Configurar Variáveis de Ambiente

No painel do Railway, adicione:

```env
# Backend
SECRET_KEY=sua_chave_secreta_super_segura_aqui
DATABASE_URL=postgresql://... (automático)
REDIS_URL=redis://... (se usar Redis)

# APIs de Pagamento (opcional)
PIX_API_KEY=sua_chave_pix
PIX_API_SECRET=seu_secret_pix

# Email (opcional)
SENDGRID_API_KEY=sua_chave_sendgrid
```

### 5. Deploy Automático
- Railway fará deploy automaticamente
- Backend estará em: `https://seu-backend.railway.app`
- Frontend estará em: `https://seu-frontend.railway.app`

## 🔧 Estrutura do Projeto

```
sinuca-real-railway/
├── backend/                 # API Flask
│   ├── src/
│   │   └── main.py         # Aplicação principal
│   ├── requirements.txt    # Dependências Python
│   ├── Procfile           # Comando de execução
│   └── railway.json       # Configuração Railway
├── frontend/               # Interface React
│   ├── src/
│   ├── package.json       # Dependências Node.js
│   └── railway.json       # Configuração Railway
├── database/
│   └── init.sql           # Script de inicialização
└── README.md              # Este arquivo
```

## 💰 Custos no Railway

### Desenvolvimento (Hobby)
- **$5/mês** por serviço
- **2 serviços** = $10/mês total
- **500 horas** de execução incluídas

### Produção (Pro)
- **$20/mês** base + uso
- **Escalabilidade** automática
- **Domínio personalizado**

## 🔒 Segurança Automática

Railway fornece automaticamente:
- ✅ **HTTPS/SSL** em todos os domínios
- ✅ **Isolamento** de containers
- ✅ **Backup automático** do banco
- ✅ **Logs centralizados**
- ✅ **Monitoramento** integrado

## 📊 Funcionalidades

### Sistema de Apostas
- **Taxa de 5%** da plataforma
- **Apostas peer-to-peer**
- **Sistema de escrow** seguro
- **Cálculo automático** de prêmios

### Interface Moderna
- **Design responsivo**
- **Sistema de níveis**
- **Carteira virtual**
- **Estatísticas em tempo real**

### API Completa
- **RESTful API** documentada
- **Rate limiting** automático
- **Validação** de dados
- **Logs detalhados**

## 🛠️ Desenvolvimento Local

### Backend
```bash
cd backend
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd frontend
pnpm install
pnpm run dev
```

## 🔄 Atualizações

1. **Commit** suas mudanças no GitHub
2. **Push** para o repositório
3. **Railway** faz deploy automático
4. **Verificar** logs no painel

## 📈 Monitoramento

### Métricas Automáticas
- **CPU e Memória** em tempo real
- **Requests por minuto**
- **Tempo de resposta**
- **Erros e logs**

### Alertas
- **Email** para erros críticos
- **Slack/Discord** integração
- **Webhook** personalizado

## 🎯 Próximos Passos

### Após Deploy
1. **Testar** todas as funcionalidades
2. **Configurar** domínio personalizado
3. **Integrar** gateway de pagamento
4. **Configurar** email SMTP
5. **Adicionar** monitoramento avançado

### Escalabilidade
- **Auto-scaling** baseado em CPU
- **Load balancer** automático
- **CDN** para assets estáticos
- **Cache Redis** para performance

## 📞 Suporte

### Documentação
- **Railway Docs:** https://docs.railway.app
- **Logs:** Painel do Railway
- **Métricas:** Dashboard integrado

### Troubleshooting
- **Build falha:** Verificar logs de build
- **App não inicia:** Verificar variáveis de ambiente
- **Banco não conecta:** Verificar DATABASE_URL
- **Frontend não carrega:** Verificar build do React

## 🎉 Vantagens do Railway

### vs Servidor Tradicional
- ✅ **10x mais rápido** para configurar
- ✅ **Sem configuração** de servidor
- ✅ **SSL automático**
- ✅ **Backup automático**
- ✅ **Escalabilidade** automática
- ✅ **Monitoramento** incluído

### vs Outras Plataformas
- ✅ **Mais simples** que AWS/GCP
- ✅ **Mais barato** que Heroku
- ✅ **Melhor DX** que DigitalOcean
- ✅ **Deploy mais rápido** que Vercel+Backend

---

**Criado por:** Manus AI  
**Data:** 22 de junho de 2025  
**Versão:** 1.0 Railway

🚀 **Pronto para deploy em 5 minutos!**

