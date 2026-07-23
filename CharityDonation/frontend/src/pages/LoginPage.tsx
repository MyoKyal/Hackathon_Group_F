import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../api/client";
import { useLanguage } from "../contexts/LanguageContext";
import { Mail, Lock, Eye, EyeOff, Loader2, HeartHandshake, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("login.failed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      {/* Left Section: Hero */}
      <div className="auth-hero">
        <h2>Welcome Back to Our Community.</h2>
        <p>Sign in to continue making an impact and connecting with vital resources. Your continued support drives our mission forward.</p>
        
        <div className="stats">
          <div className="stat-item">
            <HeartHandshake className="stat-icon" size={48} />
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#0f172a' }}>Make an Impact</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Every connection matters</div>
            </div>
          </div>
          <div className="stat-item">
            <ShieldCheck className="stat-icon" size={48} />
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#0f172a' }}>Secure Platform</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Your data is protected</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section: Auth Card */}
      <div className="auth-form-container">
        <div className="auth-card">
          <h1 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>{t("login.title")}</h1>
          <p className="auth-subtitle" style={{ textAlign: 'center' }}>
            Welcome back! Sign in to continue making an impact.
          </p>

          <form onSubmit={handleSubmit}>
            <label>
              {t("login.email")}
              <div className="input-wrapper">
                <Mail className="input-icon" size={20} />
                <input 
                  type="email" 
                  required 
                  placeholder="john@example.com"
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                />
              </div>
            </label>
            
            <label>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{t("login.password")}</span>
                <Link to="#" className="muted" style={{ fontSize: '0.8rem', fontWeight: 500 }}>
                  Forgot password?
                </Link>
              </div>
              <div className="input-wrapper">
                <Lock className="input-icon" size={20} />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button 
                  type="button" 
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </label>
            
            {error && <div className="error">{error}</div>}
            
            <button type="submit" disabled={submitting} style={{ marginTop: '0.5rem', width: '100%' }}>
              {submitting ? (
                <>
                  <Loader2 size={20} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  {t("login.button.submitting")}
                </>
              ) : (
                t("login.button")
              )}
            </button>
          </form>
          
          <p className="muted" style={{ textAlign: 'center', marginTop: '2rem' }}>
            {t("login.no_account")} <Link to="/signup" style={{ fontWeight: 600 }}>{t("nav.signup")}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
