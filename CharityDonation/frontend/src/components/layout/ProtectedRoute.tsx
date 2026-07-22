import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) return <div className="container">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return <Outlet />;
}

export function VolunteerRoute() {
  const { user, loading } = useAuth();

  if (loading) return <div className="container">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_volunteer || user.volunteer_status !== "approved") {
    return <Navigate to="/volunteer/apply" replace />;
  }

  return <Outlet />;
}

export function AdminRoute() {
  const { user, loading } = useAuth();

  if (loading) return <div className="container">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_admin) return <Navigate to="/" replace />;

  return <Outlet />;
}
