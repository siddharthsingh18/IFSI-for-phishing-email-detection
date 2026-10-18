import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

export interface SelectOption<T = string | number> {
  value: T;
  label: string;
  description?: string;
  badge?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface SelectProps<T = string | number> {
  options: SelectOption<T>[];
  value: T;
  onChange: (value: T) => void;
  label?: string;
  helperText?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  buttonClassName?: string;
  menuClassName?: string;
  size?: 'sm' | 'md';
  align?: 'left' | 'right';
  id?: string;
  ariaLabel?: string;
  renderTriggerLabel?: (selected: SelectOption<T> | undefined) => React.ReactNode;
}

export function Select<T extends string | number>({
  options,
  value,
  onChange,
  label,
  helperText,
  placeholder = 'Select option...',
  disabled = false,
  className = '',
  buttonClassName = '',
  menuClassName = '',
  size = 'md',
  align = 'left',
  id,
  ariaLabel,
  renderTriggerLabel,
}: SelectProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value);

  // Close when clicking outside or pressing Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleSelect = (optionValue: T, optionDisabled?: boolean) => {
    if (optionDisabled) return;
    onChange(optionValue);
    setIsOpen(false);
  };

  const isSmall = size === 'sm';

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {label && (
        <label
          htmlFor={id}
          className="block text-xs font-semibold text-slate-300 mb-1.5"
        >
          {label}
        </label>
      )}

      {/* Select Trigger Button */}
      <button
        type="button"
        id={id}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label={ariaLabel || label}
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={`w-full rounded-xl bg-slate-950 border transition-all duration-150 flex items-center justify-between text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 active:scale-[0.99] ${
          isOpen
            ? 'border-teal-500/60 ring-1 ring-teal-500/30 bg-slate-900/60 shadow-md'
            : 'border-slate-800 hover:border-slate-700 hover:bg-slate-900/40'
        } ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        } ${
          isSmall
            ? 'px-2.5 py-1.5 text-xs'
            : 'px-3.5 py-2 text-xs sm:text-sm text-slate-200'
        } ${buttonClassName}`}
      >
        <span className="flex items-center gap-2 flex-1 min-w-0 mr-1.5 overflow-hidden">
          {renderTriggerLabel ? (
            renderTriggerLabel(selectedOption)
          ) : selectedOption ? (
            <>
              {selectedOption.icon && (
                <span className="flex-shrink-0 text-teal-400">
                  {selectedOption.icon}
                </span>
              )}
              <span className="truncate text-slate-200 font-medium">
                {selectedOption.label}
              </span>
              {selectedOption.badge && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-mono font-semibold flex-shrink-0">
                  {selectedOption.badge}
                </span>
              )}
            </>
          ) : (
            <span className="text-slate-500">{placeholder}</span>
          )}
        </span>

        {/* Animated Rotating Chevron */}
        <ChevronDown
          className={`h-4 w-4 flex-shrink-0 transition-transform duration-200 ease-out ${
            isOpen ? 'rotate-180 text-teal-400' : 'text-slate-400'
          }`}
        />
      </button>

      {helperText && (
        <p className="mt-1 text-[11px] text-slate-400">{helperText}</p>
      )}

      {/* Floating Animated Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            role="listbox"
            tabIndex={-1}
            initial={{ opacity: 0, y: -4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
            className={`absolute z-50 mt-1.5 rounded-xl bg-slate-900/95 border border-slate-800/90 shadow-2xl backdrop-blur-md p-1 overflow-hidden min-w-full ${
              align === 'right' ? 'right-0' : 'left-0'
            } max-h-64 overflow-y-auto ${menuClassName}`}
            style={{
              boxShadow:
                '0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 8px 10px -6px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
            }}
          >
            {options.map((option) => {
              const isSelected = option.value === value;
              return (
                <button
                  key={String(option.value)}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  disabled={option.disabled}
                  onClick={() => handleSelect(option.value, option.disabled)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all duration-120 flex items-center justify-between gap-3 group ${
                    option.disabled
                      ? 'opacity-40 cursor-not-allowed'
                      : isSelected
                      ? 'bg-teal-500/15 text-teal-200 font-semibold border-l-2 border-teal-400 shadow-sm'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white cursor-pointer'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {option.icon && (
                        <span
                          className={`flex-shrink-0 ${
                            isSelected ? 'text-teal-400' : 'text-slate-400 group-hover:text-teal-300'
                          }`}
                        >
                          {option.icon}
                        </span>
                      )}
                      <span className="truncate">{option.label}</span>
                      {option.badge && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700/60 font-mono font-medium">
                          {option.badge}
                        </span>
                      )}
                    </div>
                    {option.description && (
                      <p
                        className={`text-[11px] mt-0.5 truncate ${
                          isSelected ? 'text-teal-300/80' : 'text-slate-400'
                        }`}
                      >
                        {option.description}
                      </p>
                    )}
                  </div>

                  {isSelected && (
                    <Check className="h-3.5 w-3.5 text-teal-400 flex-shrink-0 ml-1" />
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
