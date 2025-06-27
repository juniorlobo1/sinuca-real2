import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Wallet, Trophy, Users, Plus, Play, DollarSign, TrendingUp, Star } from 'lucide-react'
import poolLogo from './assets/pool-logo.png'
import './App.css'

function App() {
  const [user, setUser] = useState({
    id: 'user123',
    username: 'Jogador Pro',
    wallet_balance: 250.00,
    skill_rating: 1450,
    total_games: 45,
    games_won: 32,
    total_earnings: 1250.00
  })

  const [availableBets, setAvailableBets] = useState([
    {
      id: 'bet1',
      player1_id: 'player1',
      player1_name: 'Carlos Silva',
      bet_amount: 25.00,
      platform_fee: 2.50,
      total_prize: 47.50,
      skill_rating: 1380,
      created_at: '2025-06-22T04:10:00Z'
    },
    {
      id: 'bet2',
      player1_id: 'player2',
      player1_name: 'Ana Costa',
      bet_amount: 50.00,
      platform_fee: 5.00,
      total_prize: 95.00,
      skill_rating: 1520,
      created_at: '2025-06-22T04:05:00Z'
    },
    {
      id: 'bet3',
      player1_id: 'player3',
      player1_name: 'Roberto Lima',
      bet_amount: 10.00,
      platform_fee: 1.00,
      total_prize: 19.00,
      skill_rating: 1200,
      created_at: '2025-06-22T04:00:00Z'
    }
  ])

  const [newBetAmount, setNewBetAmount] = useState('')
  const [isCreateBetOpen, setIsCreateBetOpen] = useState(false)

  const calculateBetDetails = (amount) => {
    const totalPool = amount * 2
    const platformFee = totalPool * 0.05
    const prize = totalPool - platformFee
    return { totalPool, platformFee, prize }
  }

  const createBet = () => {
    const amount = parseFloat(newBetAmount)
    if (amount > 0 && amount <= user.wallet_balance) {
      const { platformFee, prize } = calculateBetDetails(amount)
      const newBet = {
        id: `bet${Date.now()}`,
        player1_id: user.id,
        player1_name: user.username,
        bet_amount: amount,
        platform_fee: platformFee,
        total_prize: prize,
        skill_rating: user.skill_rating,
        created_at: new Date().toISOString()
      }
      setAvailableBets([newBet, ...availableBets])
      setUser(prev => ({ ...prev, wallet_balance: prev.wallet_balance - amount }))
      setNewBetAmount('')
      setIsCreateBetOpen(false)
    }
  }

  const acceptBet = (bet) => {
    if (user.wallet_balance >= bet.bet_amount) {
      setUser(prev => ({ ...prev, wallet_balance: prev.wallet_balance - bet.bet_amount }))
      setAvailableBets(prev => prev.filter(b => b.id !== bet.id))
      // Simular início da partida
      alert(`Aposta aceita! Iniciando partida contra ${bet.player1_name}`)
    }
  }

  const getSkillLevel = (rating) => {
    if (rating < 1000) return { level: 'Bronze', color: 'bg-amber-600' }
    if (rating < 1300) return { level: 'Prata', color: 'bg-gray-400' }
    if (rating < 1600) return { level: 'Ouro', color: 'bg-yellow-500' }
    if (rating < 2000) return { level: 'Platina', color: 'bg-blue-500' }
    return { level: 'Diamante', color: 'bg-purple-600' }
  }

  const winRate = user.total_games > 0 ? (user.games_won / user.total_games * 100).toFixed(1) : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src={poolLogo} alt="Sinuca Real" className="w-10 h-10" />
              <div>
                <h1 className="text-2xl font-bold text-white">Sinuca Real</h1>
                <p className="text-sm text-blue-200">Sistema de Apostas</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-300">Bem-vindo,</p>
                <p className="font-semibold text-white">{user.username}</p>
              </div>
              <div className="flex items-center space-x-2 bg-green-600/20 px-3 py-2 rounded-lg border border-green-500/30">
                <Wallet className="w-4 h-4 text-green-400" />
                <span className="font-bold text-green-400">R$ {user.wallet_balance.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs defaultValue="lobby" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-black/20 border border-white/10">
            <TabsTrigger value="lobby" className="data-[state=active]:bg-blue-600">
              <Users className="w-4 h-4 mr-2" />
              Lobby
            </TabsTrigger>
            <TabsTrigger value="wallet" className="data-[state=active]:bg-blue-600">
              <Wallet className="w-4 h-4 mr-2" />
              Carteira
            </TabsTrigger>
            <TabsTrigger value="stats" className="data-[state=active]:bg-blue-600">
              <Trophy className="w-4 h-4 mr-2" />
              Estatísticas
            </TabsTrigger>
            <TabsTrigger value="game" className="data-[state=active]:bg-blue-600">
              <Play className="w-4 h-4 mr-2" />
              Jogar
            </TabsTrigger>
          </TabsList>

          {/* Lobby Tab */}
          <TabsContent value="lobby" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-white">Apostas Disponíveis</h2>
              <Dialog open={isCreateBetOpen} onOpenChange={setIsCreateBetOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-green-600 hover:bg-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Criar Aposta
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-800 border-slate-700">
                  <DialogHeader>
                    <DialogTitle className="text-white">Criar Nova Aposta</DialogTitle>
                    <DialogDescription className="text-gray-300">
                      Defina o valor da sua aposta. A plataforma retém 5% do total como taxa.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="bet-amount" className="text-white">Valor da Aposta (R$)</Label>
                      <Input
                        id="bet-amount"
                        type="number"
                        placeholder="0.00"
                        value={newBetAmount}
                        onChange={(e) => setNewBetAmount(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    {newBetAmount && !isNaN(parseFloat(newBetAmount)) && (
                      <div className="bg-blue-900/30 p-4 rounded-lg border border-blue-500/30">
                        <h4 className="font-semibold text-blue-300 mb-2">Detalhes da Aposta:</h4>
                        <div className="space-y-1 text-sm text-gray-300">
                          <p>Sua aposta: R$ {parseFloat(newBetAmount).toFixed(2)}</p>
                          <p>Aposta do oponente: R$ {parseFloat(newBetAmount).toFixed(2)}</p>
                          <p>Total do pool: R$ {(parseFloat(newBetAmount) * 2).toFixed(2)}</p>
                          <p>Taxa da plataforma (5%): R$ {(parseFloat(newBetAmount) * 2 * 0.05).toFixed(2)}</p>
                          <p className="font-semibold text-green-400">Prêmio para o vencedor: R$ {(parseFloat(newBetAmount) * 2 * 0.95).toFixed(2)}</p>
                        </div>
                      </div>
                    )}
                    <Button onClick={createBet} className="w-full bg-green-600 hover:bg-green-700">
                      Criar Aposta
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-4">
              {availableBets.map((bet) => {
                const skillLevel = getSkillLevel(bet.skill_rating)
                return (
                  <Card key={bet.id} className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-bold text-lg">
                              {bet.player1_name.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <h3 className="font-semibold text-white">{bet.player1_name}</h3>
                            <div className="flex items-center space-x-2">
                              <Badge className={`${skillLevel.color} text-white`}>
                                {skillLevel.level}
                              </Badge>
                              <span className="text-sm text-gray-400">Rating: {bet.skill_rating}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">R$ {bet.total_prize.toFixed(2)}</div>
                          <div className="text-sm text-gray-400">Prêmio</div>
                          <div className="text-xs text-gray-500">Aposta: R$ {bet.bet_amount.toFixed(2)} cada</div>
                        </div>
                        
                        <Button 
                          onClick={() => acceptBet(bet)}
                          className="bg-blue-600 hover:bg-blue-700"
                          disabled={user.wallet_balance < bet.bet_amount}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          Aceitar
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* Wallet Tab */}
          <TabsContent value="wallet" className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Carteira Virtual</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-gradient-to-br from-green-600 to-green-800 border-green-500">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Wallet className="w-5 h-5 mr-2" />
                    Saldo Atual
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-white">R$ {user.wallet_balance.toFixed(2)}</div>
                  <p className="text-green-100">Disponível para apostas</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-blue-600 to-blue-800 border-blue-500">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Ganhos Totais
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-white">R$ {user.total_earnings.toFixed(2)}</div>
                  <p className="text-blue-100">Lucro acumulado</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Depositar Fundos</CardTitle>
                  <CardDescription className="text-gray-400">
                    Adicione dinheiro à sua carteira virtual
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="deposit-amount" className="text-white">Valor (R$)</Label>
                    <Input
                      id="deposit-amount"
                      type="number"
                      placeholder="0.00"
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    <DollarSign className="w-4 h-4 mr-2" />
                    Depositar via PIX
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Sacar Fundos</CardTitle>
                  <CardDescription className="text-gray-400">
                    Transfira seus ganhos para sua conta
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="withdraw-amount" className="text-white">Valor (R$)</Label>
                    <Input
                      id="withdraw-amount"
                      type="number"
                      placeholder="0.00"
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>
                  <Button className="w-full bg-orange-600 hover:bg-orange-700">
                    <DollarSign className="w-4 h-4 mr-2" />
                    Sacar via PIX
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Stats Tab */}
          <TabsContent value="stats" className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Suas Estatísticas</h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Trophy className="w-5 h-5 mr-2" />
                    Partidas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{user.total_games}</div>
                  <p className="text-gray-400">Total jogadas</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Star className="w-5 h-5 mr-2" />
                    Vitórias
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-400">{user.games_won}</div>
                  <p className="text-gray-400">{winRate}% de aproveitamento</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Rating</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-400">{user.skill_rating}</div>
                  <Badge className={`${getSkillLevel(user.skill_rating).color} text-white mt-2`}>
                    {getSkillLevel(user.skill_rating).level}
                  </Badge>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Game Tab */}
          <TabsContent value="game" className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Mesa de Jogo</h2>
            
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-6">
                <div className="text-center space-y-4">
                  <div className="w-full h-64 bg-green-800 rounded-lg border-4 border-amber-700 flex items-center justify-center">
                    <p className="text-white text-lg">Mesa de Sinuca Real</p>
                  </div>
                  <p className="text-gray-400">
                    Aceite uma aposta no lobby para começar a jogar!
                  </p>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    Ir para o Lobby
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

