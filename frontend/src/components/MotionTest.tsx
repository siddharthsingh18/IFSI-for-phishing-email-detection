import React from 'react';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, scaleIn } from '../lib/motion';

/**
 * Test component confirming shared motion variants and framer-motion imports.
 */
export const MotionTest: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      <motion.div variants={fadeInUp}>
        <motion.div variants={scaleIn}>
          {children || <span>Motion test component initialized</span>}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default MotionTest;
