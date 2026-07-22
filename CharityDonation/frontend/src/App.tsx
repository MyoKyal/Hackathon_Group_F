import { Route, Routes } from "react-router-dom";
import { Header } from "./components/layout/Header";
import { AdminRoute, ProtectedRoute, VolunteerRoute } from "./components/layout/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import HomePage from "./pages/HomePage";
import DonatePage from "./pages/DonatePage";
import RequestPage from "./pages/RequestPage";
import MyDonationsPage from "./pages/MyDonationsPage";
import MyRequestsPage from "./pages/MyRequestsPage";
import BrowseDonationsPage from "./pages/BrowseDonationsPage";
import BrowseRequestsPage from "./pages/BrowseRequestsPage";
import VolunteerApplyPage from "./pages/VolunteerApplyPage";
import VolunteerDashboardPage from "./pages/VolunteerDashboardPage";
import DeliveryDetailPage from "./pages/DeliveryDetailPage";
import MatchesPage from "./pages/MatchesPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/donate" element={<DonatePage />} />
          <Route path="/request" element={<RequestPage />} />
          <Route path="/my-donations" element={<MyDonationsPage />} />
          <Route path="/my-requests" element={<MyRequestsPage />} />
          <Route path="/donations/all" element={<BrowseDonationsPage />} />
          <Route path="/requests/all" element={<BrowseRequestsPage />} />
          <Route path="/volunteer/apply" element={<VolunteerApplyPage />} />
          <Route path="/matches" element={<MatchesPage />} />
          <Route path="/deliveries/:id" element={<DeliveryDetailPage />} />
        </Route>

        <Route element={<VolunteerRoute />}>
          <Route path="/volunteer/dashboard" element={<VolunteerDashboardPage />} />
        </Route>

        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Routes>
    </>
  );
}
