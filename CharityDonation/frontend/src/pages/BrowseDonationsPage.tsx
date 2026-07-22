import { useQuery } from "@tanstack/react-query";
import { listAllDonations } from "../api/donations";

export default function BrowseDonationsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["donations-all"],
    queryFn: listAllDonations,
  });

  return (
    <div className="container">
      <h1>Browse All Donations</h1>
      {isLoading && <p className="muted">Loading...</p>}
      {error && <p className="error">Failed to load donations.</p>}
      {data && data.length === 0 && <p className="muted">No donations yet.</p>}
      {data?.map((d) => (
        <div className="card" key={d.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <strong>{d.item_name}</strong>
            <span className="badge">{d.status}</span>
          </div>
          <div className="muted">
            {d.item_category} · qty {d.quantity} · donated by {d.donor_name}
          </div>
        </div>
      ))}
    </div>
  );
}
