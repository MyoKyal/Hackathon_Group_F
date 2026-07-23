import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../api/client";
import { useLanguage } from "../contexts/LanguageContext";
import { User, Mail, Lock, Phone, Eye, EyeOff, Loader2, HeartHandshake } from "lucide-react";

export default function SignupPage() {
  const { signup } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "", full_name: "", phone: "" });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signup({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        phone: form.phone || undefined,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("signup.failed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      {/* Left Section: Hero */}
      <div className="auth-hero">
        <h2>Together, We Can Make a Difference.</h2>
        <p>Join our community and help connect people with the support and resources they need. Every small act of kindness counts.</p>
        
        <div className="stats">
          <div className="stat-item">
            <HeartHandshake className="stat-icon" size={48} />
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>10k+</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Donations Made</div>
            </div>
          </div>
          <div className="stat-item">
            <User className="stat-icon" size={48} />
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>5k+</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Active Volunteers</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section: Form */}
      <div className="auth-form-container">
        <div className="auth-card">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
            <HeartHandshake size={40} color="var(--primary)" />
          </div>
          <h1 style={{ textAlign: 'center' }}>Create your account</h1>
          <p className="auth-subtitle" style={{ textAlign: 'center' }}>
            Join our community and start making an impact.
          </p>

          <form onSubmit={handleSubmit}>
            <label>
              {t("signup.full_name")}
              <div className="input-wrapper">
                <User className="input-icon" size={20} />
                <input
                  required
                  placeholder="John Doe"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                />
              </div>
            </label>
            
            <label>
              {t("signup.email")}
              <div className="input-wrapper">
                <Mail className="input-icon" size={20} />
                <input
                  type="email"
                  required
                  placeholder="john@example.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
            </label>
            
            <label>
              {t("signup.password")}
              <div className="input-wrapper">
                <Lock className="input-icon" size={20} />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={8}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
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
            
            <label>
              {t("signup.phone")}
              <div className="input-wrapper">
                <Phone className="input-icon" size={20} />
                <input 
                  placeholder="+1 (555) 000-0000"
                  value={form.phone} 
                  onChange={(e) => setForm({ ...form, phone: e.target.value })} 
                />
              </div>
            </label>

            {error && <div className="error">{error}</div>}
            
            <button type="submit" disabled={submitting} style={{ marginTop: '0.5rem', width: '100%' }}>
              {submitting ? (
                <>
                  <Loader2 size={20} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  {t("signup.button.submitting")}
                </>
              ) : (
                t("signup.button")
              )}
            </button>
          </form>

          <p className="muted" style={{ textAlign: 'center', marginTop: '2rem' }}>
            {t("signup.has_account")} <Link to="/login" style={{ fontWeight: 600 }}>{t("nav.login")}</Link>
          </p>
          <p className="muted" style={{ textAlign: 'center', fontSize: '0.75rem', marginTop: '1rem' }}>
            By creating an account, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
