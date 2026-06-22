/** Animated page wrapper using Framer Motion */
import { motion } from 'framer-motion';

const variants = {
  initial:  { opacity: 0, y: 18 },
  animate:  { opacity: 1, y: 0,  transition: { duration: 0.35, ease: [0.25, 0.46, 0.45, 0.94] } },
  exit:     { opacity: 0, y: -12, transition: { duration: 0.2 } },
};

export default function PageWrapper({ children, className = '' }) {
  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={`page ${className}`}
    >
      {children}
    </motion.div>
  );
}
