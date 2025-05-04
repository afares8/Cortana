import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { BugIcon, SendIcon, InfoIcon } from "lucide-react";
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  intent?: string;
  isLoading?: boolean;
  debugInfo?: any;
}

export function AIContextualChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      text: 'Hola, soy tu asistente legal. ¿En qué puedo ayudarte hoy?',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/v1/ai/contextual-generate`, {
        query: input,
        user_id: 1, // In a real app, this would be the actual user ID
        debug: debugMode
      });

      const aiResponse = response.data;
      
      setMessages(prev => prev.map(msg => 
        msg.isLoading ? {
          id: msg.id,
          text: aiResponse.generated_text,
          sender: 'ai',
          timestamp: new Date(),
          intent: aiResponse.intent,
          debugInfo: debugMode ? {
            original_query: aiResponse.original_query,
            enhanced_prompt: aiResponse.enhanced_prompt,
            context_data: aiResponse.context_data,
            debug_info: aiResponse.debug_info
          } : undefined
        } : msg
      ));
    } catch (error) {
      console.error('Error sending message:', error);
      
      setMessages(prev => prev.map(msg => 
        msg.isLoading ? {
          id: msg.id,
          text: 'Lo siento, hubo un error al procesar tu consulta. Por favor, intenta de nuevo más tarde.',
          sender: 'ai',
          timestamp: new Date()
        } : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleDebugMode = () => {
    setDebugMode(!debugMode);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Asistente Legal Contextual</CardTitle>
        <CardDescription>
          Consulta información sobre tareas, contratos, clientes y reportes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[calc(100vh-300px)] pr-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className="max-w-[80%]">
                  {message.isLoading ? (
                    <div className="flex justify-center p-2">
                      <div className="animate-spin h-5 w-5 border-2 border-zinc-500 rounded-full border-t-transparent"></div>
                    </div>
                  ) : (
                    <div className={`rounded-lg p-3 ${message.sender === 'user' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700'}`}>
                      <div className="whitespace-pre-wrap text-sm">
                        {message.text}
                      </div>
                      
                      {message.intent && (
                        <div className="mt-2 flex items-center gap-2">
                          <Badge variant="outline" className="capitalize">
                            {message.intent}
                          </Badge>
                        </div>
                      )}
                      
                      {message.debugInfo && (
                        <div className="mt-3">
                          <Separator className="my-2" />
                          <div className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">
                            Debug Information
                          </div>
                          
                          <div className="mt-2">
                            <div className="text-xs font-semibold">
                              Original Query:
                            </div>
                            <div className="text-xs ml-2">
                              {message.debugInfo.original_query}
                            </div>
                          </div>
                          
                          {message.debugInfo.debug_info && (
                            <div className="mt-2">
                              <div className="text-xs font-semibold">
                                Intent Confidence: {message.debugInfo.debug_info.confidence.toFixed(2)}
                              </div>
                              <div className="text-xs font-semibold">
                                Parameters:
                              </div>
                              <div className="text-xs ml-2">
                                {Object.keys(message.debugInfo.debug_info.parameters || {}).length > 0 
                                  ? JSON.stringify(message.debugInfo.debug_info.parameters, null, 2)
                                  : "None"}
                              </div>
                            </div>
                          )}
                          
                          {message.debugInfo.context_data && (
                            <div className="mt-2">
                              <div className="text-xs font-semibold">
                                Context Data:
                              </div>
                              <pre className="text-xs ml-2 max-h-[100px] overflow-auto bg-zinc-200 dark:bg-zinc-900 p-1 rounded text-[0.65rem]">
                                {JSON.stringify(message.debugInfo.context_data, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="text-xs text-zinc-500 dark:text-zinc-400 ml-1 mt-1">
                    {!message.isLoading && new Intl.DateTimeFormat('es', {
                      hour: '2-digit',
                      minute: '2-digit'
                    }).format(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        
        <div className="flex items-center gap-2 mt-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="debug-mode"
              checked={debugMode}
              onCheckedChange={toggleDebugMode}
            />
            <Label htmlFor="debug-mode" className="text-sm flex items-center gap-1">
              <BugIcon className="h-4 w-4" />
              Modo Debug
            </Label>
          </div>
        </div>
        
        <div className="flex items-end gap-2 mt-2">
          <Textarea
            placeholder="Escribe tu consulta aquí..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isLoading}
            className="min-h-[80px] resize-none"
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4"
          >
            <SendIcon className="h-4 w-4 mr-2" />
            Enviar
          </Button>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between border-t pt-4">
        <div className="flex items-center text-xs text-zinc-500 dark:text-zinc-400">
          <InfoIcon className="h-3 w-3 mr-1" />
          Puedes preguntar sobre tareas pendientes, contratos, clientes, o reportes de cumplimiento.
        </div>
      </CardFooter>
    </Card>
  );
}

export default AIContextualChat;
