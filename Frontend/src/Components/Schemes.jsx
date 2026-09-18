import { Link } from "react-router-dom";
import "./Schemes.css";

// `scheme` is a dashboard entry shaped by the backend's /api/dashboard
// response: scheme_id, scheme_name, final_score, description, applied.
function Scheme({ scheme }) {

  const scoreClass = scheme.final_score >= 75 ? "high" : "medium";

  return (
    <Link to={`/dashboard/scheme/${scheme.scheme_id}`} className="scheme-row">

      <div className="scheme-header">

        <h3>
          {scheme.scheme_name}
          {scheme.applied && <span className="applied-badge">Applied</span>}
        </h3>

        <div className={`dual-score ${scoreClass}`}>
          {scheme.final_score}%
        </div>

      </div>

      <p className="scheme-description">
        {scheme.description}
      </p>

      <span className="scheme-view-link">View details →</span>

    </Link>
  );
}

export default Scheme;
