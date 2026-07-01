import { useState } from 'react';
import { Zap, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from './AuthProvider';

interface SignupPageProps {
  onSwitchToLogin: () => void;
}

export function SignupPage({ onSwitchToLogin }: SignupPageProps) {
  const { signup } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [agreed, setAgreed] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }
    if (!agreed) {
      setError('Please agree to the terms & conditions');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      await signup(name, email, password);
    } catch {
      setError('Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-bg-orb auth-bg-orb-1" />
        <div className="auth-bg-orb auth-bg-orb-2" />
        <div className="auth-bg-orb auth-bg-orb-3" />
      </div>
      <div className="auth-card">
        <div className="auth-card-header">
          <div className="auth-logo">
            <Zap size={28} />
            <span>SmartNotes</span>
          </div>
          <h1>Create your account</h1>
          <p>Start organizing your thoughts intelligently</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {error && <div className="auth-error">{error}</div>}

          <div className="auth-input-group">
            <User size={16} className="auth-input-icon" />
            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
              id="signup-name"
            />
          </div>

          <div className="auth-input-group">
            <Mail size={16} className="auth-input-icon" />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              id="signup-email"
            />
          </div>

          <div className="auth-input-group">
            <Lock size={16} className="auth-input-icon" />
            <input
              type="password"
              placeholder="Password (min. 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              id="signup-password"
            />
          </div>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              id="signup-terms"
            />
            <span>I agree to the Terms of Service and Privacy Policy</span>
          </label>

          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={isLoading}
            id="signup-submit"
          >
            {isLoading ? (
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              <>
                Create Account
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <span>Already have an account?</span>
          <button className="auth-link" onClick={onSwitchToLogin}>
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}
