import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import Icon from '@/components/ui/icon';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

type Request = {
  id: string;
  text: string;
  response: string;
  timestamp: string;
  status: 'completed' | 'pending';
};

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [requestText, setRequestText] = useState('');
  const [requests, setRequests] = useState<Request[]>([
    {
      id: '1',
      text: 'Создай изображение космоса',
      response: 'Изображение создано успешно',
      timestamp: '2 часа назад',
      status: 'completed',
    },
  ]);

  const freeLimit = 2;
  const usedRequests = 1;
  const isPremium = false;

  const handleSendRequest = () => {
    if (!requestText.trim()) return;
    
    const newRequest: Request = {
      id: Date.now().toString(),
      text: requestText,
      response: 'Обрабатывается...',
      timestamp: 'только что',
      status: 'pending',
    };
    
    setRequests([newRequest, ...requests]);
    setRequestText('');
    
    setTimeout(() => {
      setRequests(prev =>
        prev.map(req =>
          req.id === newRequest.id
            ? { ...req, response: 'Ответ готов!', status: 'completed' as const }
            : req
        )
      );
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-6xl mx-auto p-4 md:p-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
              <Icon name="Bot" size={28} className="text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Neiro Bot</h1>
              <p className="text-sm text-muted-foreground">Панель управления</p>
            </div>
          </div>
          <Avatar className="w-10 h-10">
            <AvatarFallback className="bg-secondary text-secondary-foreground">
              <Icon name="User" size={20} />
            </AvatarFallback>
          </Avatar>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-card">
            <TabsTrigger value="dashboard" className="gap-2">
              <Icon name="LayoutDashboard" size={16} />
              <span className="hidden sm:inline">Главная</span>
            </TabsTrigger>
            <TabsTrigger value="requests" className="gap-2">
              <Icon name="MessageSquare" size={16} />
              <span className="hidden sm:inline">Запросы</span>
            </TabsTrigger>
            <TabsTrigger value="premium" className="gap-2">
              <Icon name="Crown" size={16} />
              <span className="hidden sm:inline">Premium</span>
            </TabsTrigger>
            <TabsTrigger value="profile" className="gap-2">
              <Icon name="User" size={16} />
              <span className="hidden sm:inline">Профиль</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6 animate-fade-in">
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="border-border/40">
                <CardHeader className="pb-3">
                  <CardDescription>Использовано запросов</CardDescription>
                  <CardTitle className="text-3xl">{usedRequests}/{isPremium ? '∞' : freeLimit}</CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress value={(usedRequests / freeLimit) * 100} className="h-2" />
                </CardContent>
              </Card>

              <Card className="border-border/40">
                <CardHeader className="pb-3">
                  <CardDescription>Текущий тариф</CardDescription>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    {isPremium ? (
                      <>
                        <Icon name="Crown" size={24} className="text-primary" />
                        Premium
                      </>
                    ) : (
                      <>
                        <Icon name="Sparkles" size={24} className="text-muted-foreground" />
                        Бесплатный
                      </>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {!isPremium && (
                    <Button
                      onClick={() => setActiveTab('premium')}
                      className="w-full bg-primary hover:bg-primary/90"
                    >
                      Улучшить
                    </Button>
                  )}
                </CardContent>
              </Card>

              <Card className="border-border/40">
                <CardHeader className="pb-3">
                  <CardDescription>Всего запросов</CardDescription>
                  <CardTitle className="text-3xl">{requests.length}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">История сохранена</p>
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/40">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon name="Zap" size={20} />
                  Быстрый запрос
                </CardTitle>
                <CardDescription>Создайте новый запрос к нейросети</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Опишите ваш запрос..."
                  value={requestText}
                  onChange={(e) => setRequestText(e.target.value)}
                  className="min-h-[100px] resize-none bg-muted/30"
                />
                <Button
                  onClick={handleSendRequest}
                  disabled={!requestText.trim() || (!isPremium && usedRequests >= freeLimit)}
                  className="w-full bg-primary hover:bg-primary/90"
                >
                  <Icon name="Send" size={16} className="mr-2" />
                  Отправить запрос
                </Button>
                {!isPremium && usedRequests >= freeLimit && (
                  <p className="text-sm text-destructive text-center">
                    Лимит бесплатных запросов исчерпан. Оформите Premium для продолжения.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card className="border-border/40">
              <CardHeader>
                <CardTitle>Последние запросы</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {requests.slice(0, 3).map((req) => (
                    <div
                      key={req.id}
                      className="p-4 rounded-lg bg-muted/30 border border-border/40 space-y-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium">{req.text}</p>
                        <Badge
                          variant={req.status === 'completed' ? 'default' : 'secondary'}
                          className="shrink-0"
                        >
                          {req.status === 'completed' ? 'Готово' : 'Обработка'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{req.response}</p>
                      <p className="text-xs text-muted-foreground">{req.timestamp}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="requests" className="space-y-6 animate-fade-in">
            <Card className="border-border/40">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon name="MessageSquare" size={20} />
                  Все запросы
                </CardTitle>
                <CardDescription>История ваших обращений к нейросети</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {requests.map((req) => (
                    <div
                      key={req.id}
                      className="p-4 rounded-lg bg-muted/30 border border-border/40 space-y-2 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <p className="text-sm font-medium mb-1">{req.text}</p>
                          <p className="text-sm text-muted-foreground">{req.response}</p>
                        </div>
                        <Badge
                          variant={req.status === 'completed' ? 'default' : 'secondary'}
                          className="shrink-0"
                        >
                          {req.status === 'completed' ? 'Готово' : 'Обработка'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">{req.timestamp}</p>
                        <Button variant="ghost" size="sm">
                          <Icon name="ExternalLink" size={14} />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="premium" className="space-y-6 animate-fade-in">
            <Card className="border-primary/40 bg-gradient-to-br from-primary/5 to-transparent">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
                    <Icon name="Crown" size={24} className="text-primary-foreground" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl">Premium подписка</CardTitle>
                    <CardDescription>Безлимитный доступ к нейросети</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <Icon name="Infinity" size={16} className="text-primary" />
                    </div>
                    <p className="text-sm">Безлимитные запросы</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <Icon name="Zap" size={16} className="text-primary" />
                    </div>
                    <p className="text-sm">Приоритетная обработка</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <Icon name="Shield" size={16} className="text-primary" />
                    </div>
                    <p className="text-sm">Расширенная поддержка</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <Icon name="History" size={16} className="text-primary" />
                    </div>
                    <p className="text-sm">Полная история запросов</p>
                  </div>
                </div>

                <div className="p-6 rounded-xl bg-card border border-border/40 space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold">499 ₽</p>
                    <p className="text-sm text-muted-foreground">в месяц</p>
                  </div>
                  
                  <div className="space-y-3">
                    <Input
                      placeholder="Номер карты для оплаты"
                      defaultValue="22007019953811"
                      disabled
                      className="bg-muted/30"
                    />
                    <Button className="w-full bg-primary hover:bg-primary/90 h-12">
                      <Icon name="CreditCard" size={18} className="mr-2" />
                      Оформить Premium
                    </Button>
                  </div>

                  <p className="text-xs text-center text-muted-foreground">
                    Безопасная оплата. Отменить можно в любой момент
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile" className="space-y-6 animate-fade-in">
            <Card className="border-border/40">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon name="User" size={20} />
                  Профиль пользователя
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4">
                  <Avatar className="w-20 h-20">
                    <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                      <Icon name="User" size={32} />
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-lg">Пользователь</p>
                    <p className="text-sm text-muted-foreground">ID: 12345678</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Telegram ID</label>
                    <Input value="@username" disabled className="bg-muted/30" />
                  </div>

                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Дата регистрации</label>
                    <Input value="15 января 2026" disabled className="bg-muted/30" />
                  </div>

                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Тариф</label>
                    <div className="flex items-center gap-2">
                      <Input
                        value={isPremium ? 'Premium' : 'Бесплатный'}
                        disabled
                        className="bg-muted/30"
                      />
                      {!isPremium && (
                        <Button onClick={() => setActiveTab('premium')} variant="outline">
                          <Icon name="Crown" size={16} />
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Статистика</label>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                        <p className="text-xs text-muted-foreground mb-1">Всего запросов</p>
                        <p className="text-xl font-bold">{requests.length}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                        <p className="text-xs text-muted-foreground mb-1">Осталось</p>
                        <p className="text-xl font-bold">
                          {isPremium ? '∞' : `${freeLimit - usedRequests}`}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-border/40">
                  <Button variant="outline" className="w-full">
                    <Icon name="HelpCircle" size={16} className="mr-2" />
                    Поддержка и FAQ
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
