import React, { useEffect, useRef, useState } from 'react';
import { syntheticSpecimens } from '../content/specimen';
import { brand } from '../content/brand';
import { useTheme } from '../hooks/useTheme';

export const HeroSpecimen: React.FC = () => {
  const { isDark } = useTheme();
  const [specimenIndex, setSpecimenIndex] = useState(0);
  const [modelView, setModelView] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [hintVisible, setHintVisible] = useState(true);
  const [lensSeen, setLensSeen] = useState<Set<number>>(new Set());
  const [reducedMotion, setReducedMotion] = useState(false);
  const sheetRef = useRef<HTMLDivElement>(null);
  const lens = useRef({ x: 50, y: 50 });
  const frame = useRef<number | null>(null);
  const current = syntheticSpecimens[specimenIndex];
  const injectedLines = current.footer.filter((line) => line.injected);
  const allRevealed = reducedMotion || revealed || isDark;

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => {
      setReducedMotion(media.matches);
      if (media.matches) setRevealed(true);
    };
    update();
    media.addEventListener('change', update);
    const timer = window.setTimeout(() => setHintVisible(false), 3600);
    return () => {
      media.removeEventListener('change', update);
      window.clearTimeout(timer);
      if (frame.current !== null) cancelAnimationFrame(frame.current);
    };
  }, []);

  const updateLens = (clientX: number, clientY: number) => {
    const element = sheetRef.current;
    if (!element) return;
    const rect = element.getBoundingClientRect();
    lens.current = {
      x: ((clientX - rect.left) / rect.width) * 100,
      y: ((clientY - rect.top) / rect.height) * 100,
    };
    if (frame.current === null) {
      frame.current = requestAnimationFrame(() => {
        if (sheetRef.current) {
          sheetRef.current.style.setProperty('--lens-x', `${lens.current.x}%`);
          sheetRef.current.style.setProperty('--lens-y', `${lens.current.y}%`);
          const lines = sheetRef.current.querySelectorAll<HTMLElement>('[data-injected-index]');
          const next = new Set(lensSeen);
          lines.forEach((line) => {
            const lineRect = line.getBoundingClientRect();
            if (Math.abs(lineRect.top + lineRect.height / 2 - (rectTop(rect) + rect.height * lens.current.y / 100)) < 28) {
              next.add(Number(line.dataset.injectedIndex));
            }
          });
          if (next.size !== lensSeen.size) setLensSeen(next);
        }
        frame.current = null;
      });
    }
  };

  const rectTop = (rect: DOMRect) => rect.top;
  const changeSpecimen = () => {
    setSpecimenIndex((index) => (index + 1) % syntheticSpecimens.length);
    setLensSeen(new Set());
    setRevealed(false);
    setModelView(false);
  };

  const renderLines = (uv = false) => (
    <div className={`hero-specimen-copy ${modelView ? 'hero-specimen-copy--model' : ''}`}>
      <div className="hero-specimen-headers">
        <div><span>From:</span> {current.sender}</div>
        <div><span>To:</span> {current.recipient}</div>
        <div><span>Subject:</span> {current.subject}</div>
      </div>
      <div className="hero-specimen-body">
        {current.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      </div>
      <div className="hero-specimen-footer">
        {current.footer.map((line, index) => (
          <div
            key={line.text}
            data-injected-index={line.injected ? index : undefined}
            className={`hero-specimen-line ${line.injected ? 'is-injected' : ''} ${allRevealed && line.injected ? 'is-revealed' : ''}`}
          >
            <span aria-hidden="true">{line.text}</span>
            {line.injected && (
              <span className="sr-only">Hidden instruction: {line.text}. Goal: {line.goal}.</span>
            )}
            {line.injected && (allRevealed || lensSeen.has(index)) && !uv && (
              <span className="hero-evidence-tag">Tells the model to {line.goal === 'skip check' ? 'skip the link check' : line.goal === 'force verdict' ? 'force a verdict' : 'suppress the report'}</span>
            )}
            {uv && line.injected && <span className="hero-uv-goal">{line.goal}</span>}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="hero-specimen-stage">
      <div
        ref={sheetRef}
        tabIndex={0}
        role="img"
        aria-label={`Synthetic Northwind Payroll email specimen: ${current.label}. Focus and move the lens to inspect hidden instructions.`}
        className={`hero-specimen-sheet ${modelView ? 'is-model-view' : ''}`}
        onPointerMove={(event) => updateLens(event.clientX, event.clientY)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') setModelView((value) => !value);
          if (event.key === 'Escape') setHintVisible(false);
          if (event.key.toLowerCase() === 'g') changeSpecimen();
          if (event.key.startsWith('Arrow')) {
            event.preventDefault();
            const rect = sheetRef.current?.getBoundingClientRect();
            if (rect) {
              const x = rect.left + rect.width * lens.current.x / 100 + (event.key === 'ArrowLeft' ? -24 : event.key === 'ArrowRight' ? 24 : 0);
              const y = rect.top + rect.height * lens.current.y / 100 + (event.key === 'ArrowUp' ? -24 : event.key === 'ArrowDown' ? 24 : 0);
              updateLens(x, y);
            }
          }
        }}
        style={{ '--lens-x': `${lens.current.x}%`, '--lens-y': `${lens.current.y}%` } as React.CSSProperties}
      >
        <div className="hero-specimen-base">{renderLines()}</div>
        <div className="hero-specimen-uv" aria-hidden="true">{renderLines(true)}</div>
        <div className="hero-specimen-bracket" aria-hidden="true">Everything the model reads</div>
        <div className="hero-specimen-file-tag">{brand.creditLine}</div>
        {hintVisible && !reducedMotion && (
          <div className="hero-lens-hint">Move your cursor over the sheet</div>
        )}
      </div>
      <div className="hero-specimen-controls" role="radiogroup" aria-label="Specimen reading mode">
        <button type="button" role="radio" aria-checked={!modelView} onClick={() => setModelView(false)} className={!modelView ? 'is-selected' : ''}>Human view</button>
        <button type="button" role="radio" aria-checked={modelView} onClick={() => setModelView(true)} className={modelView ? 'is-selected' : ''}>Model view</button>
      </div>
      <div className="hero-specimen-caption" aria-live="polite">
        {modelView ? 'To the model, small and faint text reads the same as everything else.' : allRevealed ? `${injectedLines.length} hidden instructions found.` : current.id === 'clean-payroll' ? 'This clean specimen has no hidden instructions.' : 'Drag across the sheet to inspect it.'}
      </div>
      <button type="button" className="hero-reveal-toggle" onClick={() => setRevealed((value) => !value)}>
        {allRevealed ? 'Hide hidden instructions' : 'Show hidden instructions'}
      </button>
    </div>
  );
};
