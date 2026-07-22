import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <header>
      <Link to="/" style={{ fontWeight: 600, textDecoration: "none", color: "inherit" }}>
        Charity Donation
      </Link>
      <nav>
        {user ? (
          <>
            <Link to="/donate">Donate</Link>
            <Link to="/request">Request</Link>
            <Link to="/my-donations">My Donations</Link>
            <Link to="/my-requests">My Requests</Link>
            <Link to="/donations/all">Browse Donations</Link>
            <Link to="/requests/all">Browse Requests</Link>
            <Link to="/matches">Matches</Link>
            {user.is_volunteer && user.volunteer_status === "approved" ? (
              <Link to="/volunteer/dashboard">Volunteer Dashboard</Link>
            ) : (
              <Link to="/volunteer/apply">Become a Volunteer</Link>
            )}
            {user.is_admin && <Link to="/admin">Admin</Link>}
            <span className="muted">{user.full_name}</span>
            <button className="secondary" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Link to="/signup">Sign up</Link>
          </>
        )}
      </nav>
    </header>
  );
}
