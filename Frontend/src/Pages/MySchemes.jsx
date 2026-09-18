import { useEffect, useState } from "react";
import Scheme from "../Components/Schemes";
import { api } from "../api/client";

function MySchemes() {
  const [state, setState] = useState({ status: "loading", schemes: [], error: "" });

  useEffect(() => {
    let cancelled = false;
    api
      .mySchemes()
      .then((data) => {
        if (!cancelled) setState({ status: "ready", schemes: data.schemes || [], error: "" });
      })
      .catch((err) => {
        if (!cancelled) setState({ status: "error", schemes: [], error: err.message || "Could not load your schemes" });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="scheme-dashboard">

      <div className="dashboard-title">
        <h1>My Schemes</h1>
        <p>Schemes you've applied to</p>
      </div>

      {state.status === "loading" && <p className="scheme-list-empty">Loading…</p>}

      {state.status === "error" && <p className="scheme-list-empty">{state.error}</p>}

      {state.status === "ready" && state.schemes.length === 0 && (
        <p className="scheme-list-empty">
          You haven't applied to any schemes yet — head back to the dashboard to explore what's available.
        </p>
      )}

      {state.status === "ready" && state.schemes.length > 0 && (
        <div className="scheme-list">
          {state.schemes.map((scheme) => (
            <Scheme key={scheme.scheme_id} scheme={scheme} />
          ))}
        </div>
      )}

    </section>
  );
}

export default MySchemes;
