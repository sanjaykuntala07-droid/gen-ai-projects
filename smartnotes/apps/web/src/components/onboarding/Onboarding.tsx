import { useState, useEffect } from 'react';
import { Zap, FileText, Tag, Bell, Sparkles, Search, ArrowRight, X } from 'lucide-react';

const ONBOARDING_KEY = 'smartnotes_onboarding_dismissed';

const steps = [
  {
    icon: <Zap size={40} />,
    title: 'Welcome to SmartNotes',
    description: 'Your intelligent note-taking companion with rich editing, tags, reminders, and AI assistance.',
    color: 'var(--color-accent)',
  },
  {
    icon: <FileText size={40} />,
    title: 'Create & Organize Notes',
    description: 'Use the quick-add bar to create notes instantly. Rich block editing with headings, lists, code blocks, and more.',
    color: 'var(--color-success)',
  },
  {
    icon: <Tag size={40} />,
    title: 'Tag Everything',
    description: 'Color-coded tags help you organize and filter notes. Create tags on the fly while editing.',
    color: 'hsl(280, 70%, 60%)',
  },
  {
    icon: <Bell size={40} />,
    title: 'Never Forget',
    description: 'Set reminders on any note. Quick options for 1 hour, tomorrow, or next week — plus custom scheduling.',
    color: 'var(--color-warning)',
  },
  {
    icon: <Sparkles size={40} />,
    title: 'AI-Powered',
    description: 'Summarize notes, auto-tag content, get writing suggestions, and improve your text — all powered by AI.',
    color: 'hsl(340, 80%, 60%)',
  },
  {
    icon: <Search size={40} />,
    title: 'Find Anything',
    description: 'Full-text search with highlighted snippets. Press ⌘K to search from anywhere.',
    color: 'var(--color-accent)',
  },
];

export function Onboarding() {
  const [visible, setVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const dismissed = localStorage.getItem(ONBOARDING_KEY);
    if (!dismissed) {
      setVisible(true);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setVisible(false);
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleDismiss();
    }
  };

  if (!visible) return null;

  const step = steps[currentStep];

  return (
    <>
      <div className="onboarding-backdrop" />
      <div className="onboarding-modal" id="onboarding">
        <button className="onboarding-skip" onClick={handleDismiss}>
          <X size={18} /> Skip
        </button>

        <div className="onboarding-content">
          <div className="onboarding-icon" style={{ color: step.color }}>
            {step.icon}
          </div>
          <h2>{step.title}</h2>
          <p>{step.description}</p>
        </div>

        <div className="onboarding-footer">
          <div className="onboarding-dots">
            {steps.map((_, i) => (
              <span
                key={i}
                className={`onboarding-dot ${i === currentStep ? 'active' : ''}`}
                onClick={() => setCurrentStep(i)}
              />
            ))}
          </div>
          <button className="btn btn-primary" onClick={handleNext}>
            {currentStep < steps.length - 1 ? (
              <>Next <ArrowRight size={16} /></>
            ) : (
              <>Get Started <ArrowRight size={16} /></>
            )}
          </button>
        </div>
      </div>
    </>
  );
}
