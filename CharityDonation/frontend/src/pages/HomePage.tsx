import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useLanguage } from "../contexts/LanguageContext";
import { Heart, Package, Users, ArrowRight } from "lucide-react";

export default function HomePage() {
  const { user } = useAuth();
  const { t } = useLanguage();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Dynamic Hero Section with Background Image */}
      <section className="hero-section" style={{ backgroundImage: "url('/images/hero-bg.jpg')", padding: '6rem 2rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
        <div className="bg-overlay-navy"></div>
        <div className="hero-content" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ 
            fontSize: '3.5rem', 
            fontWeight: 900, 
            marginBottom: '1.5rem', 
            lineHeight: 1.2, 
            letterSpacing: '-0.02em', 
            background: 'linear-gradient(135deg, #F24361, #288BEF)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.3))'
          }}>
            {t("home.hero.title")}
          </h1>
          <p style={{ fontSize: '1.25rem', marginBottom: '2.5rem', opacity: 0.9, lineHeight: 1.6, textShadow: '0 2px 4px rgba(0,0,0,0.5)', color: '#FAFAFA' }}>
            {t("home.hero.subtitle")}
          </p>
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {user ? (
              <>
                <Link to="/donate" style={{ textDecoration: 'none' }}>
                  <button className="btn-coral" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem', padding: '1rem 2rem' }}>
                    <Heart size={20} /> {t("home.hero.donate_btn")}
                  </button>
                </Link>
                <Link to="/request" style={{ textDecoration: 'none' }}>
                  <button style={{ background: 'transparent', border: '2px solid #FAFAFA', color: '#FAFAFA', fontWeight: 700, borderRadius: '9999px', padding: '1rem 2rem', fontSize: '1.1rem', transition: 'all 0.2s ease', backdropFilter: 'blur(4px)' }}>
                    {t("home.hero.request_btn")}
                  </button>
                </Link>
              </>
            ) : (
              <>
                <Link to="/signup" style={{ textDecoration: 'none' }}>
                  <button className="btn-coral" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem', padding: '1rem 2rem' }}>
                    {t("home.hero.join_btn")}
                  </button>
                </Link>
                <Link to="/login" style={{ textDecoration: 'none' }}>
                  <button style={{ background: 'rgba(30, 37, 54, 0.6)', border: '2px solid #FAFAFA', color: '#FAFAFA', fontWeight: 700, borderRadius: '9999px', padding: '1rem 2rem', fontSize: '1.1rem', backdropFilter: 'blur(8px)' }}>
                    {t("nav.login")}
                  </button>
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section style={{ padding: '5rem 2rem', background: 'var(--bg)', color: 'var(--text)', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '3rem', color: 'var(--navy)' }}>{t("home.how_it_works")}</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
          
          <div className="card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: '#F24361', color: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', boxShadow: '0 4px 10px rgba(242, 67, 97, 0.3)' }}>
              <Heart size={40} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--navy)' }}>{t("home.give.title")}</h3>
            <p style={{ color: 'var(--text-muted)' }}>{t("home.give.desc")}</p>
          </div>

          <div className="card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: '#288BEF', color: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', boxShadow: '0 4px 10px rgba(40, 139, 239, 0.3)' }}>
              <Package size={40} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--navy)' }}>{t("home.req.title")}</h3>
            <p style={{ color: 'var(--text-muted)' }}>{t("home.req.desc")}</p>
          </div>

          <div className="card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--navy)', color: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', boxShadow: '0 4px 10px rgba(30, 37, 54, 0.3)' }}>
              <Users size={40} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--navy)' }}>{t("home.vol.title")}</h3>
            <p style={{ color: 'var(--text-muted)' }}>{t("home.vol.desc")}</p>
          </div>

        </div>
      </section>

      {/* Secondary Image Banner Section */}
      <section className="hero-section" style={{ backgroundImage: "url('/images/community-1.jpg')", padding: '5rem 2rem', textAlign: 'center' }}>
        <div className="bg-overlay-navy" style={{ backgroundColor: 'rgba(30, 37, 54, 0.85)' }}></div>
        <div className="hero-content" style={{ maxWidth: '700px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1.5rem', color: '#FAFAFA' }}>{t("home.ready.title")}</h2>
          <p style={{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.9 }}>
            {t("home.ready.desc")}
          </p>
          <Link to="/donations/all" style={{ textDecoration: 'none' }}>
            <button className="btn-primary-navy" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0 auto' }}>
              {t("home.ready.btn")} <ArrowRight size={18} />
            </button>
          </Link>
        </div>
      </section>

    </div>
  );
}
