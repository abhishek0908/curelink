import React, { useState, type KeyboardEvent } from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TagInputProps {
    label: string;
    value: string[];
    onChange: (tags: string[]) => void;
    placeholder?: string;
}

const TagInput: React.FC<TagInputProps> = ({ label, value = [], onChange, placeholder }) => {
    const [input, setInput] = useState('');

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTag();
        } else if (e.key === 'Backspace' && !input && value.length > 0) {
            removeTag(value.length - 1);
        }
    };

    const addTag = () => {
        const trimmed = input.trim();
        if (trimmed && !value.includes(trimmed)) {
            onChange([...value, trimmed]);
            setInput('');
        }
    };

    const removeTag = (index: number) => {
        onChange(value.filter((_, i) => i !== index));
    };

    return (
        <div className="mb-4">
            <label className="mb-1.5 block text-sm font-medium text-slate-300">{label}</label>
            <div className="flex flex-wrap items-center gap-2 p-2 min-h-[42px] border border-slate-800 rounded-lg bg-slate-900 focus-within:ring-2 focus-within:ring-yellow-500/50 focus-within:border-yellow-500/50 transition-all">
                <AnimatePresence mode="popLayout">
                    {value.map((tag, index) => (
                        <motion.span
                            key={`${tag}-${index}`}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            layout
                            className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-yellow-500/10 text-yellow-500 border border-yellow-500/20"
                        >
                            {tag}
                            <button
                                type="button"
                                onClick={() => removeTag(index)}
                                className="ml-1.5 inline-flex flex-shrink-0 rounded-full hover:bg-yellow-500/20 transition-colors"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </motion.span>
                    ))}
                </AnimatePresence>
                <input
                    type="text"
                    className="flex-1 min-w-[120px] outline-none text-sm text-slate-100 bg-transparent placeholder:text-slate-600"
                    placeholder={value.length === 0 ? (placeholder || 'Type and press Enter...') : ''}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onBlur={addTag}
                />
            </div>
        </div>
    );
};

export default TagInput;
