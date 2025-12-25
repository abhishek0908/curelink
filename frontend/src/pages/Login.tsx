import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { PageTransition } from '../components/PageTransition';
import { Activity } from 'lucide-react';

const Login = () => {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { login, user } = useAuth();
    const navigate = useNavigate();

    React.useEffect(() => {
        if (user) {
            if (user.onboarding_completed) {
                navigate('/chat');
            } else {
                navigate('/onboarding');
            }
        }
    }, [user, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            await login(email);
        } catch (err) {
            setError('Login failed. Please check your email and try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-yellow-500/5 rounded-full blur-3xl" />
            </div>

            <PageTransition className="w-full max-w-md relative z-10">
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 rounded-2xl shadow-2xl">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="p-3 bg-yellow-500/10 rounded-xl border border-yellow-500/20">
                                <Activity className="w-8 h-8 text-yellow-500" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-yellow-200 to-yellow-500">
                            Welcome Back
                        </h2>
                        <p className="mt-2 text-sm text-slate-400">
                            Sign in to access your health dashboard
                        </p>
                    </div>

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <Input
                            label="Email address"
                            type="email"
                            required
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            error={error}
                        />

                        <Button
                            type="submit"
                            className="w-full"
                            isLoading={isSubmitting}
                        >
                            {isSubmitting ? 'Signing in...' : 'Sign in'}
                        </Button>
                    </form>
                </div>
            </PageTransition>
        </div>
    );
};

export default Login;
