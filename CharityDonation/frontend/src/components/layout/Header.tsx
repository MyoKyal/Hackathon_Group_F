import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useLanguage } from "../../contexts/LanguageContext";
import { useTheme } from "../../contexts/ThemeContext";
import { Menu, X, LogOut, ChevronDown, Heart, HandHeart, List, Sun, Moon } from "lucide-react";

// Custom SVG Logo for "Warm Hug"
const WarmHugLogo = () => (
  <svg width="40" height="40" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* Left Heart (Warm Coral Red) */}
    <path d="M50 85 C10 55, 0 35, 20 15 C35 0, 50 20, 50 30" fill="none" stroke="#F24361" strokeWidth="12" strokeLinecap="round" />
    <path d="M50 85 C10 55, 0 35, 20 15" fill="none" stroke="#F24361" strokeWidth="12" strokeLinecap="round" />
    
    {/* Right Heart (Bright Sky Blue) */}
    <path d="M50 85 C90 55, 100 35, 80 15 C65 0, 50 20, 50 30" fill="none" stroke="#288BEF" strokeWidth="12" strokeLinecap="round" />
    <path d="M50 85 C90 55, 100 35, 80 15" fill="none" stroke="#288BEF" strokeWidth="12" strokeLinecap="round" />
    
    {/* Center Figure (Warm Coral Red) */}
    <circle cx="50" cy="40" r="8" fill="#F24361" />
    <path d="M50 55 C40 55, 30 50, 30 50 L50 85 L70 50 C70 50, 60 55, 50 55 Z" fill="#F24361" />
  </svg>
);

export function Header() {
  const { user, logout } = useAuth();
  const { t, language, setLanguage } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const toggleMenu = () => setMobileMenuOpen(!mobileMenuOpen);

  return (
    <header style={{ 
      background: 'var(--bg)',
      borderBottom: '1px solid var(--border)',
      padding: '1rem 2rem', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between', 
      position: 'relative',
      zIndex: 1000
    }}>
      <Link to="/" className="notranslate" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 800, textDecoration: "none", fontSize: '1.75rem', letterSpacing: '-0.03em' }}>
        <WarmHugLogo />
        <div style={{ display: 'flex' }}>
          <span style={{ color: 'var(--text)' }}>Warm</span>
          <span style={{ color: '#F24361', marginLeft: '0.35rem' }}>Hug</span>
        </div>
      </Link>
      
      <button className="mobile-menu-btn" onClick={toggleMenu} aria-label="Toggle menu" style={{ color: 'var(--text)', background: 'transparent', border: 'none' }}>
        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <nav className={mobileMenuOpen ? "mobile-open" : ""} style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        {user ? (
          <>
            <Link to="/donate" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>{t("nav.donate")}</Link>
            <Link to="/request" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>{t("nav.request")}</Link>
            
            {/* Dropdown: Donations */}
            <div className="nav-dropdown">
              <div className="nav-dropdown-trigger" style={{ fontWeight: 600, color: 'var(--text)' }}>
                Donations <ChevronDown size={16} />
              </div>
              <div className="nav-dropdown-menu" style={{ background: 'var(--card-bg)', borderColor: 'var(--border)' }}>
                <Link to="/donations/all" className="nav-dropdown-item" onClick={toggleMenu} style={{ color: 'var(--text)' }}>
                  <List size={18} /> Browse All
                </Link>
                <Link to="/donations/me" className="nav-dropdown-item" onClick={toggleMenu} style={{ color: 'var(--text)' }}>
                  <Heart size={18} /> My Donations
                </Link>
              </div>
            </div>

            {/* Dropdown: Requests */}
            <div className="nav-dropdown">
              <div className="nav-dropdown-trigger" style={{ fontWeight: 600, color: 'var(--text)' }}>
                Requests <ChevronDown size={16} />
              </div>
              <div className="nav-dropdown-menu" style={{ background: 'var(--card-bg)', borderColor: 'var(--border)' }}>
                <Link to="/requests/all" className="nav-dropdown-item" onClick={toggleMenu} style={{ color: 'var(--text)' }}>
                  <List size={18} /> Browse All
                </Link>
                <Link to="/requests/me" className="nav-dropdown-item" onClick={toggleMenu} style={{ color: 'var(--text)' }}>
                  <HandHeart size={18} /> My Requests
                </Link>
              </div>
            </div>

            <Link to="/matches" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>{t("nav.matches")}</Link>
            
            {user.is_volunteer && user.volunteer_status === "approved" ? (
              <Link to="/volunteer/dashboard" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>Dispatch</Link>
            ) : (
              <Link to="/volunteer/apply" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>Volunteer</Link>
            )}
            
            {user.is_admin && <Link to="/admin" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>Admin</Link>}
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: 'auto' }}>
              
              {/* Theme Toggle Button */}
              <button 
                onClick={toggleTheme}
                style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '0.4rem', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
                aria-label="Toggle Theme"
              >
                {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
              </button>

              <div className="avatar-badge" style={{ background: 'var(--card-bg)', color: 'var(--text)', border: '1px solid var(--border)' }}>
                <div className="avatar-circle" style={{ background: '#288BEF', color: '#FAFAFA' }}>
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                </div>
                <span>{user.full_name}</span>
              </div>
              <button 
                onClick={handleLogout} 
                style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', color: 'var(--text)', padding: '0.5rem', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', transition: 'all 0.2s ease' }}
                aria-label={t("nav.logout")}
                title={t("nav.logout")}
              >
                <LogOut size={16} />
              </button>
            </div>
          </>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <button 
              onClick={toggleTheme}
              style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '0.4rem', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
            <Link to="/login" onClick={toggleMenu} style={{ fontWeight: 600, color: 'var(--text)' }}>{t("nav.login")}</Link>
            <Link to="/signup" style={{ background: '#F24361', color: '#FAFAFA', padding: '0.5rem 1.25rem', borderRadius: '9999px', fontWeight: 700 }} onClick={toggleMenu}>{t("nav.signup")}</Link>
          </div>
        )}
        
        {/* Language Toggle */}
        <select 
          value={language} 
          onChange={(e) => setLanguage(e.target.value as 'en' | 'mm')}
          style={{ padding: '0.4rem 0.5rem', marginLeft: mobileMenuOpen ? '0' : '0.5rem', marginTop: mobileMenuOpen ? '1rem' : '0', borderRadius: '6px', border: '1px solid var(--border)', fontSize: '0.85rem', cursor: 'pointer', background: 'var(--card-bg)', color: 'var(--text)' }}
        >
          <option value="en" style={{ color: 'black' }}>EN</option>
          <option value="mm" style={{ color: 'black' }}>MM</option>
        </select>
      </nav>
    </header>
  );
}
