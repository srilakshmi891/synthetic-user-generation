import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export function LoadingSpinner({ message = 'Generating personas…' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="relative h-16 w-16"
      >
        <div className="absolute inset-0 rounded-full border-4 border-brand-100" />
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-brand-600 border-r-accent-500" />
        <Sparkles className="absolute inset-0 m-auto h-6 w-6 text-brand-600" />
      </motion.div>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mt-6 text-sm font-medium text-slate-600"
      >
        {message}
      </motion.p>
      <motion.div className="mt-4 flex gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-2 w-2 rounded-full bg-brand-400"
            animate={{ opacity: [0.3, 1, 0.3], y: [0, -4, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </motion.div>
    </div>
  );
}
