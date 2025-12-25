import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../lib/axios';
import TagInput from '../components/TagInput';
import { PageTransition } from '../components/PageTransition';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { ChevronRight, Save } from 'lucide-react';
import { motion } from 'framer-motion';

interface OnboardingData {
    full_name: string;
    age: number | '';
    gender: string;
    previous_diseases: string[];
    current_symptoms: string[];
    medications: string[];
    allergies: string[];
    additional_notes: string;
}

const initialData: OnboardingData = {
    full_name: '',
    age: '',
    gender: '',
    previous_diseases: [],
    current_symptoms: [],
    medications: [],
    allergies: [],
    additional_notes: '',
};

const Onboarding = () => {
    const { user, updateUser } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState<OnboardingData>(initialData);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [mode, setMode] = useState<'create' | 'update'>('create');
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/onboarding');
                if (response.data && Object.keys(response.data).length > 0) {
                    const d = response.data;
                    setFormData({
                        full_name: d.full_name || '',
                        age: d.age || '',
                        gender: d.gender || '',
                        previous_diseases: d.previous_diseases || [],
                        current_symptoms: d.current_symptoms || [],
                        medications: d.medications || [],
                        allergies: d.allergies || [],
                        additional_notes: d.additional_notes || ''
                    });
                    setMode('update');
                }
            } catch (err) {
                // ignore
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: name === 'age' ? (value === '' ? '' : parseInt(value)) : value,
        }));
    };

    const handleListChange = (key: keyof OnboardingData) => (value: string[]) => {
        setFormData((prev) => ({ ...prev, [key]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSaving(true);

        if (!formData.full_name || !formData.age || !formData.gender) {
            setError("Please fill in the required fields (Name, Age, Gender)");
            setSaving(false);
            return;
        }

        try {
            if (mode === 'create') {
                await api.post('/onboarding', formData);
            } else {
                await api.patch('/onboarding', formData);
            }

            if (user) {
                updateUser({ onboarding_completed: true });
            }
            navigate('/dashboard');
        } catch (err) {
            setError('Failed to save data. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return (
        <div className="min-h-screen flex items-center justify-center text-slate-400">
            <div className="animate-pulse">Loading profile...</div>
        </div>
    );

    return (
        <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
            <PageTransition className="max-w-3xl mx-auto">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
                    <div className="relative bg-gradient-to-r from-yellow-600 to-yellow-500 px-6 sm:px-8 py-6 sm:py-8">
                        <div className="absolute top-0 right-0 p-4 opacity-10 hidden sm:block">
                            <Save size={120} />
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Patient Profile</h2>
                        <p className="text-slate-900/80 mt-1 sm:mt-2 font-medium text-sm sm:text-base">Complete your medical profile for better assistance.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="p-5 sm:p-8 space-y-6 sm:space-y-8">
                        {error && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-lg text-sm">{error}</div>}

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="space-y-6"
                        >
                            <h3 className="text-base sm:text-lg font-semibold text-white border-b border-slate-800 pb-2">Personal Information</h3>
                            <div className="grid grid-cols-1 gap-5 sm:gap-6 sm:grid-cols-2">
                                <div className="sm:col-span-2">
                                    <Input
                                        label="Full Name *"
                                        name="full_name"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <Input
                                    label="Age *"
                                    type="number"
                                    name="age"
                                    value={formData.age}
                                    onChange={handleChange}
                                    required
                                />

                                <div>
                                    <label className="mb-1.5 block text-sm font-medium text-slate-300">Gender *</label>
                                    <select
                                        name="gender"
                                        required
                                        value={formData.gender}
                                        onChange={handleChange}
                                        className="flex h-10 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50"
                                    >
                                        <option value="">Select Gender</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="space-y-6"
                        >
                            <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">Medical History</h3>

                            <TagInput
                                label="Previous Diseases"
                                value={formData.previous_diseases}
                                onChange={handleListChange('previous_diseases')}
                                placeholder="Type disease and press Enter"
                            />

                            <TagInput
                                label="Current Symptoms"
                                value={formData.current_symptoms}
                                onChange={handleListChange('current_symptoms')}
                            />

                            <TagInput
                                label="Current Medications"
                                value={formData.medications}
                                onChange={handleListChange('medications')}
                            />

                            <TagInput
                                label="Allergies"
                                value={formData.allergies}
                                onChange={handleListChange('allergies')}
                            />
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                        >
                            <label className="mb-1.5 block text-sm font-medium text-slate-300">Additional Notes</label>
                            <textarea
                                name="additional_notes"
                                rows={4}
                                value={formData.additional_notes}
                                onChange={handleChange}
                                className="block w-full rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50"
                            />
                        </motion.div>

                        <div className="flex justify-end pt-6 gap-3 border-t border-slate-800">

                            <Button
                                type="submit"
                                isLoading={saving}
                            >
                                Save & Continue <ChevronRight className="ml-2 w-4 h-4" />
                            </Button>
                        </div>
                    </form>
                </div>
            </PageTransition>
        </div>
    );
};

export default Onboarding;
