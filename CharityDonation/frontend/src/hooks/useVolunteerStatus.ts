import { useAuth } from "./useAuth";

export function useVolunteerStatus() {
  const { user } = useAuth();
  const isApprovedVolunteer = !!user?.is_volunteer && user.volunteer_status === "approved";
  return { user, isApprovedVolunteer, volunteerStatus: user?.volunteer_status ?? "none" };
}
