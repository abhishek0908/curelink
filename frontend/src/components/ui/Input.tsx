import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { InputHTMLAttributes } from 'react';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "ref"> {
    label?: string;
    error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ className, label, error, ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className="mb-1.5 block text-sm font-medium text-slate-300">
                        {label}
                    </label>
                )}
                <motion.div
                    initial={false}
                    animate={error ? { x: [0, -10, 10, -10, 10, 0] } : {}}
                    transition={{ duration: 0.4 }}
                >
                    <input
                        ref={ref}
                        className={cn(
                            'flex h-10 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200',
                            error && 'border-red-500 focus:ring-red-500/50 focus:border-red-500',
                            className
                        )}
                        {...props}
                    />
                </motion.div>
                {error && (
                    <motion.p
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-1 text-xs text-red-500"
                    >
                        {error}
                    </motion.p>
                )}
            </div>
        );
    }
);
Input.displayName = 'Input';

export { Input };
