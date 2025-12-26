import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/axios';
import { Button } from '../components/ui/Button';
import { ArrowLeft, Send, MoreVertical, Phone, Video } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCheck, Plus, Smile, Mic } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// Types
interface Message {
    id?: number | string;
    role: 'user' | 'assistant';
    content: string;
    created_at?: string;
    type?: 'text'; // future proofing
}

interface WSMessage {
    type: 'history' | 'message' | 'error';
    role?: 'user' | 'assistant';
    content?: string | any; // history content is list
    message?: string; // from API
    messages?: Array<{ role: string, content: string }>;
}

const Chat = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isTyping, setIsTyping] = useState(false);

    // Pagination state
    const [isLoadingHistory, setIsLoadingHistory] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [offset, setOffset] = useState(0);
    const limit = 20;

    const ws = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const prevScrollHeightRef = useRef<number>(0);

    // Fetch history
    const fetchHistory = useCallback(async (currentOffset: number) => {
        try {
            setIsLoadingHistory(true);
            const response = await api.get('/chat/history', {
                params: {
                    limit: limit,
                    offset: currentOffset,
                }
            });

            const apiRes = response.data;
            const data = apiRes.data || [];
            if (data.length < limit) {
                setHasMore(false);
            }

            const formattedMessages: Message[] = data.map((msg: any) => ({
                id: msg.id,
                role: msg.role,
                content: msg.message || msg.content,
                created_at: msg.created_at
            })).reverse(); // API gives newest first, we want oldest first for chat flow

            if (currentOffset === 0) {
                setMessages(formattedMessages);
                scrollToBottom('auto');
            } else {
                // Prepend messages
                setMessages(prev => [...formattedMessages, ...prev]);
                // Restore scroll position
                if (containerRef.current) {
                    const newScrollHeight = containerRef.current.scrollHeight;
                    const diff = newScrollHeight - prevScrollHeightRef.current;
                    containerRef.current.scrollTop = diff;
                }
            }

        } catch (error) {
            console.error("Failed to fetch history:", error);
        } finally {
            setIsLoadingHistory(false);
        }
    }, [limit]);

    // Initial history is loaded via WS onopen trigger
    // keeping this commented out or removing it entirely


    // Scroll handler for lazy loading
    const handleScroll = () => {
        if (!containerRef.current) return;
        const { scrollTop, scrollHeight } = containerRef.current;

        if (scrollTop === 0 && hasMore && !isLoadingHistory) {
            prevScrollHeightRef.current = scrollHeight;
            const newOffset = messages.length;
            setOffset(newOffset);
            fetchHistory(newOffset);
        }
    };

    // Initial connection logic with Auto-Reconnect
    useEffect(() => {
        if (!user?.user_id) return;

        let socket: WebSocket | null = null;
        let reconnectTimer: ReturnType<typeof setTimeout>;
        let isMounted = true;

        const connect = () => {
            if (!isMounted) return;

            const token = localStorage.getItem('token');

            // Determine WS URL
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            let wsUrl = '';

            if (apiUrl.startsWith('http')) {
                const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
                const wsHost = apiUrl.replace(/^https?:\/\//, '');
                wsUrl = `${wsProtocol}://${wsHost}/ws/chat?token=${token}`;
            } else {
                // Relative URL case (e.g. "/api") - Connect to same host
                const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
                wsUrl = `${wsProtocol}://${window.location.host}/ws/chat?token=${token}`;
            }

            socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                if (!isMounted) return;
                console.log('Connected to chat');
                setIsConnected(true);
                // Auto-refresh chat on connection (handles initial load & reconnection)
                fetchHistory(0);
            };

            socket.onmessage = (event) => {
                if (!isMounted) return;
                const data: WSMessage = JSON.parse(event.data);

                if (data.type === 'history' && data.messages) {
                    console.log("WS History received (ignoring in favor of API)");
                } else if (data.type === 'message') {
                    setIsTyping(false);
                    const newMsg: Message = {
                        id: Date.now(),
                        role: data.role as 'user' | 'assistant',
                        content: data.content as string,
                        created_at: new Date().toISOString()
                    };
                    setMessages(prev => [...prev, newMsg]);
                    scrollToBottom();
                } else if (data.type === 'error') {
                    console.error("WS Error:", data.message || "Unknown error");
                    setIsTyping(false);
                }
            };

            socket.onclose = () => {
                if (!isMounted) return;
                console.log('Disconnected. Attempting to reconnect in 3s...');
                setIsConnected(false);

                // Try to reconnect
                reconnectTimer = setTimeout(() => {
                    connect();
                }, 3000);
            };

            ws.current = socket;
        };

        connect();

        return () => {
            isMounted = false;
            clearTimeout(reconnectTimer);
            if (socket) {
                socket.onclose = null; // Prevent reconnect loop on unmount
                socket.close();
            }
        };
    }, [user?.user_id, fetchHistory]);

    const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
        // slight delay to ensure render
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior });
        }, 100);
    };

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || !ws.current) return;

        const text = inputValue.trim();

        // Optimistic update
        const userMsg: Message = {
            id: Date.now(), // temp id
            role: 'user',
            content: text,
            created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        scrollToBottom();
        setIsTyping(true); // Artificial typing indicator for "Waiting for reply"

        ws.current.send(text);
    };

    // Placeholder for history fetching
    // const fetchOlderHistory = async () => {
    //     console.log("Loading older messages...");
    // };

    // Auto-scroll on new messages removed to prevent jumping when loading history
    // Handled explicitly in socket.onmessage and fetchHistory

    return (
        <div className="flex flex-col h-screen bg-slate-950 text-gray-100 overflow-hidden">
            {/* Header */}
            <div className="bg-slate-900 border-b border-slate-800 p-3 flex items-center justify-between shrink-0 z-50 shadow-lg sticky top-0">
                <div className="flex items-center gap-2">
                    <Button variant="ghost" onClick={() => navigate('/dashboard')} className="p-2 w-10 h-10 rounded-full flex items-center justify-center hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-slate-900 font-bold text-lg shadow-inner">
                            CL
                        </div>
                        {isConnected && (
                            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-slate-900 rounded-full"></div>
                        )}
                    </div>
                    <div className="ml-1">
                        <h2 className="font-bold text-base leading-tight text-gray-100">CureLink Assistant</h2>
                        <p className="text-[11px] text-yellow-500/80 font-medium tracking-wide">
                            {isConnected ? 'online' : 'connecting...'}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-0.5 sm:gap-1 text-slate-400">
                    <Button variant="ghost" className="p-2 w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center opacity-70 hover:opacity-100 hidden xs:flex"><Video className="w-4 h-4 sm:w-5 sm:h-5" /></Button>
                    <Button variant="ghost" className="p-2 w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center opacity-70 hover:opacity-100 hidden xs:flex"><Phone className="w-4 h-4 sm:w-5 sm:h-5" /></Button>
                    <Button variant="ghost" className="p-2 w-9 h-9 flex items-center justify-center opacity-70 hover:opacity-100"><MoreVertical className="w-5 h-5" /></Button>
                </div>
            </div>

            {/* Chat Area */}
            <div
                ref={containerRef}
                onScroll={handleScroll}
                className="flex-1 overflow-y-auto px-4 py-6 space-y-2 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent relative"
                style={{
                    backgroundColor: '#0b141a',
                    backgroundImage: `url('/home/abhishekudiya/.gemini/antigravity/brain/cb083d74-3439-48a4-b9df-be820c0017e8/whatsapp_chat_bg_pattern_1766691757916.png')`,
                    backgroundSize: '400px',
                    backgroundRepeat: 'repeat',
                    backgroundBlendMode: 'overlay'
                }}
            >
                <div className="absolute inset-0 bg-slate-950/40 pointer-events-none" />

                {isLoadingHistory && offset > 0 && (
                    <div className="flex justify-center p-2 relative z-10">
                        <span className="w-5 h-5 border-2 border-yellow-500/50 border-t-yellow-500 rounded-full animate-spin"></span>
                    </div>
                )}

                <AnimatePresence initial={false}>
                    {messages.map((msg, index) => {
                        const isUser = msg.role === 'user';
                        const isFirstInSeries = index === 0 || messages[index - 1].role !== msg.role;

                        return (
                            <motion.div
                                key={msg.id || index}
                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                transition={{ duration: 0.2 }}
                                className={`flex ${isUser ? 'justify-end' : 'justify-start'} relative z-10 ${isFirstInSeries ? 'mt-4' : 'mt-1'}`}
                            >
                                <div
                                    className={`relative max-w-[90%] sm:max-w-[85%] md:max-w-[70%] px-3 py-1.5 shadow-md flex flex-col ${isUser
                                        ? 'bg-yellow-600/90 text-white rounded-2xl rounded-tr-sm'
                                        : 'bg-slate-800/95 text-gray-100 rounded-2xl rounded-tl-sm border border-slate-700/50'
                                        }`}
                                >
                                    {/* Tail for first message in series */}
                                    {isFirstInSeries && (
                                        <div className={`absolute top-0 w-2 h-2 ${isUser ? '-right-1.5 bg-yellow-600/90' : '-left-1.5 bg-slate-800/95'} clip-path-triangle`}
                                            style={{ clipPath: isUser ? 'polygon(0 0, 0 100%, 100% 0)' : 'polygon(100% 0, 100% 100%, 0 0)' }}>
                                        </div>
                                    )}

                                    <div className="pr-12 md:pr-14">
                                        {isUser ? (
                                            <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>
                                        ) : (
                                            <div className="prose prose-sm prose-invert max-w-none text-[15px] leading-relaxed
                                                prose-p:my-1.5 prose-p:leading-relaxed
                                                prose-strong:text-yellow-400 prose-strong:font-semibold
                                                prose-ul:my-2 prose-ul:ml-4 prose-ul:list-disc
                                                prose-ol:my-2 prose-ol:ml-4 prose-ol:list-decimal
                                                prose-li:my-0.5 prose-li:marker:text-yellow-500/70
                                                prose-headings:text-yellow-400 prose-headings:font-semibold prose-headings:my-2
                                                prose-code:bg-slate-700/50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-yellow-300
                                                prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700 prose-pre:rounded-lg
                                            ">
                                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                                            </div>
                                        )}
                                    </div>

                                    <div className="absolute bottom-1 right-2 flex items-center gap-1 select-none">
                                        <p className={`text-[10px] opacity-60 font-medium ${isUser ? 'text-yellow-100' : 'text-slate-400'}`}>
                                            {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }) : 'just now'}
                                        </p>
                                        {isUser && (
                                            <CheckCheck className="w-3.5 h-3.5 text-blue-300 opacity-80" />
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>

                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex justify-start relative z-10 mt-2"
                    >
                        <div className="bg-slate-800/95 border border-slate-700/50 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5 w-16 shadow-md">
                            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} className="h-2" />
            </div>

            {/* Input Area */}
            <div className="shrink-0 p-2 sm:p-3 bg-slate-900/95 backdrop-blur-md border-t border-slate-800/50 flex items-end gap-1.5 sm:gap-2">
                <div className="flex-1 bg-slate-800 rounded-3xl border border-slate-700/50 focus-within:border-yellow-500/40 transition-all flex items-center px-1.5 sm:px-2 py-0.5 sm:py-1 shadow-inner">
                    <Button variant="ghost" className="p-2 text-slate-400 hover:text-yellow-500 rounded-full hidden sm:flex">
                        <Plus className="w-5 h-5" />
                    </Button>
                    <input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={isConnected ? "Type a message..." : "Connecting..."}
                        disabled={!isConnected}
                        className="w-full bg-transparent border-none text-white px-2 py-2 sm:py-2.5 focus:ring-0 placeholder:text-slate-500 text-[14px] sm:text-[15px] disabled:opacity-50"
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(e)}
                    />
                    <Button variant="ghost" className="p-2 text-slate-400 hover:text-yellow-500 rounded-full">
                        <Smile className="w-5 h-5" />
                    </Button>
                </div>

                {inputValue.trim() ? (
                    <motion.button
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={handleSendMessage}
                        disabled={!isConnected}
                        className="w-10 h-10 sm:w-12 sm:h-12 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-full flex items-center justify-center shadow-lg transition-colors shrink-0 disabled:bg-slate-700 disabled:text-slate-500"
                    >
                        <Send className="w-5 h-5" />
                    </motion.button>
                ) : (
                    <button
                        className="w-10 h-10 sm:w-12 sm:h-12 bg-slate-800 text-slate-400 rounded-full flex items-center justify-center shadow-lg shrink-0 disabled:opacity-50"
                        disabled={!isConnected}
                    >
                        <Mic className="w-5 h-5" />
                    </button>
                )}
            </div>
        </div>
    );
};

export default Chat;
