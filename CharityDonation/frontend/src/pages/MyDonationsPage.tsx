import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listDonations } from "../api/donations";
import type { VolunteerInfo } from "../types";

function volunteerLine(label: string, info: VolunteerInfo | null | undefined) {
  if (!info) return null;
  const statusText = info.status === "accepted" ? "accepted" : "offered, not yet accepted";
  return (
    <div className="muted">
      {label}: {info.full_name} ({statusText})
    </div>
  );
}

export default function MyDonationsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["donations"],
    queryFn: listDonations,
  });

  return (
    <div className="container">
      <h1>My Donations</h1>
      {isLoading && <p className="muted">Loading...</p>}
      {error && <p className="error">Failed to load donations.</p>}
      {data && data.length === 0 && <p className="muted">You haven't submitted any donations yet.</p>}
      {data?.map((d) => (
        <div className="card" key={d.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <strong>{d.item_name}</strong>
            <span className="badge">{d.status}</span>
          </div>
          <div className="muted">
            {d.item_category} · qty {d.quantity} · warehouse: {d.warehouse.name}
          </div>
          {volunteerLine("Pickup volunteer (to warehouse)", d.pickup_volunteer)}
          {volunteerLine("Delivery volunteer (warehouse to receiver)", d.delivery?.volunteer)}
          {d.delivery && (
            <p>
              <Link to={`/deliveries/${d.delivery.id}`}>View delivery details</Link>
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
