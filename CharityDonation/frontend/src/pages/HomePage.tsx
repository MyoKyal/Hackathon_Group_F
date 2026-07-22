import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="container">
      <h1>Welcome{user ? `, ${user.full_name}` : ""}</h1>
      <p className="muted">Donate items, request items, or volunteer to deliver them.</p>
      <div className="row">
        <Link to="/donate"><button>Donate an item</button></Link>
        <Link to="/request"><button className="secondary">Request an item</button></Link>
      </div>
    </div>
  );
}
