import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { Button } from '../components/ui/Button';
import { PageTransition } from '../components/PageTransition';
import { LogOut, User, Activity, Edit2, ShieldAlert, Pill, Thermometer, History, ClipboardList, Info } from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState<any>(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/onboarding');
                setProfile(res.data);
            } catch {
                // ignore
            }
        };
        fetchProfile();
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const StatusCard = ({ label, value, icon: Icon, delay }: { label: string, value: string | number, icon: any, delay: number }) => (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay }}
            className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 p-5 rounded-2xl flex items-center gap-4 hover:border-yellow-500/30 transition-all group"
        >
            <div className="p-3 bg-slate-800 rounded-xl group-hover:bg-yellow-500/10 group-hover:text-yellow-500 transition-colors">
                <Icon className="w-6 h-6" />
            </div>
            <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
                <p className="mt-0.5 text-xl font-bold text-white leading-none">{value || 'N/A'}</p>
            </div>
        </motion.div>
    );

    const DetailSection = ({ title, icon: Icon, children, delay }: { title: string, icon: any, children: React.ReactNode, delay: number }) => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
        >
            <div className="flex items-center gap-2 mb-4">
                <Icon className="w-5 h-5 text-yellow-500" />
                <h3 className="text-lg font-semibold text-white">{title}</h3>
            </div>
            {children}
        </motion.div>
    );

    return (
        <div className="min-h-screen">
            <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <Activity className="w-6 h-6 text-yellow-500 mr-2" />
                            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-yellow-200 to-yellow-500">
                                CureLink
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center text-sm text-slate-400">
                                <User className="w-4 h-4 mr-2" />
                                {profile?.full_name || user?.user_email}
                            </div>
                            <Button
                                variant="ghost"
                                onClick={handleLogout}
                                className="text-slate-400 hover:text-white p-2 sm:px-4"
                            >
                                <LogOut className="w-5 h-5 sm:w-4 sm:h-4 sm:mr-2" />
                                <span className="hidden sm:inline">Logout</span>
                            </Button>
                        </div>
                    </div>
                </div>
            </nav>

            <PageTransition className="py-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="mb-0 sm:mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6 sm:gap-4">
                        <div>
                            <h1 className="text-2xl sm:text-3xl font-bold text-white">My Profile</h1>
                            <p className="text-slate-400 mt-2 text-sm sm:text-base leading-relaxed">Manage your personal health information</p>
                        </div>
                        <div className="flex gap-2 sm:gap-3 w-full sm:w-auto">
                            {profile && (
                                <Button onClick={() => navigate('/onboarding')} variant="outline" className="flex-1 sm:flex-none">
                                    <Edit2 className="w-4 h-4 mr-2" />
                                    Edit
                                </Button>
                            )}
                            <Button onClick={() => navigate('/chat')} className="bg-yellow-500 hover:bg-yellow-400 text-slate-900 flex-1 sm:flex-none">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-message-circle mr-2"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" /></svg>
                                Open Chat
                            </Button>
                        </div>
                    </div>

                    {profile ? (
                        <div className="space-y-6 sm:space-y-8 mt-8">
                            {/* Key Stats Row */}
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                                <StatusCard label="Age" value={profile.age} icon={User} delay={0.1} />
                                <StatusCard label="Gender" value={profile.gender} icon={Activity} delay={0.15} />
                                <StatusCard label="Meds" value={profile.medications?.length || 0} icon={Pill} delay={0.2} />
                                <StatusCard label="Allergies" value={profile.allergies?.length || 0} icon={ShieldAlert} delay={0.25} />
                            </div>

                            {/* Clinical Context */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <DetailSection title="Current Symptoms" icon={Thermometer} delay={0.3}>
                                    <div className="flex flex-wrap gap-2">
                                        {profile.current_symptoms?.map((s: string, i: number) => (
                                            <span key={i} className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 text-sm font-medium">
                                                {s}
                                            </span>
                                        ))}
                                        {!profile.current_symptoms?.length && <p className="text-slate-500 italic text-sm">No current symptoms reported</p>}
                                    </div>
                                </DetailSection>

                                <DetailSection title="Medical History" icon={History} delay={0.35}>
                                    <div className="flex flex-wrap gap-2">
                                        {profile.previous_diseases?.map((d: string, i: number) => (
                                            <span key={i} className="px-3 py-1.5 rounded-lg bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 text-sm font-medium">
                                                {d}
                                            </span>
                                        ))}
                                        {!profile.previous_diseases?.length && <p className="text-slate-500 italic text-sm">No previous diseases recorded</p>}
                                    </div>
                                </DetailSection>
                            </div>

                            {/* Detailed Lists */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <DetailSection title="Active Medications" icon={Pill} delay={0.4}>
                                    <ul className="space-y-3">
                                        {profile.medications?.map((m: string, i: number) => (
                                            <li key={i} className="flex items-center gap-3 text-slate-300 text-sm bg-slate-800/40 p-3 rounded-xl border border-slate-700/30">
                                                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                                                {m}
                                            </li>
                                        ))}
                                        {!profile.medications?.length && <p className="text-slate-500 italic text-sm">No active medications</p>}
                                    </ul>
                                </DetailSection>

                                <DetailSection title="Known Allergies" icon={ShieldAlert} delay={0.45}>
                                    <ul className="space-y-3">
                                        {profile.allergies?.map((a: string, i: number) => (
                                            <li key={i} className="flex items-center gap-3 text-slate-300 text-sm bg-slate-800/40 p-3 rounded-xl border border-slate-700/30">
                                                <div className="w-2 h-2 rounded-full bg-red-500" />
                                                {a}
                                            </li>
                                        ))}
                                        {!profile.allergies?.length && <p className="text-slate-500 italic text-sm">No known allergies</p>}
                                    </ul>
                                </DetailSection>
                            </div>

                            {/* Additional Notes */}
                            <DetailSection title="Additional Notes" icon={ClipboardList} delay={0.5}>
                                <div className="bg-slate-800/30 p-5 rounded-2xl border border-slate-800/50">
                                    <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                                        {profile.additional_notes || "No additional health notes provided."}
                                    </p>
                                </div>
                            </DetailSection>
                        </div>
                    ) : (
                        <div className="text-center py-24 bg-slate-900/50 rounded-3xl border border-slate-800 border-dashed">
                            <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
                                <Info className="w-10 h-10 text-slate-600" />
                            </div>
                            <h2 className="text-xl font-bold text-white mb-2">Profile Incomplete</h2>
                            <p className="text-slate-400 mb-8 max-w-sm mx-auto">Please complete your health profile to get better medical assistance.</p>
                            <Button onClick={() => navigate('/onboarding')} className="bg-yellow-500 hover:bg-yellow-400 text-slate-900 px-10">
                                Complete Profile
                            </Button>
                        </div>
                    )}
                </div>
            </PageTransition>

            {/* Floating button removed */}
        </div>
    );
};

export default Dashboard;
