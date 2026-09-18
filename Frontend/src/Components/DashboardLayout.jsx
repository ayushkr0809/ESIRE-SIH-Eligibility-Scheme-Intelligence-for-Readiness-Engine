import { useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { LANGUAGE_OPTIONS, languageLabel } from "./languages";
import { useAuth } from "../auth/AuthContext";
import { useLanguage } from "../i18n/LanguageContext";
import { api } from "../api/client";
import "../Pages/Scheme-Dashboard.css";

// Header title/subtitle per route — keeps the header meaningful instead of
// always saying "Scheme Discovery" no matter which page you're actually on.
const HEADER_TEXT = {
  "/dashboard": ["Scheme Discovery", "Find schemes matched to your profile"],
  "/dashboard/profile": ["My Profile", "Your details and preferences"],
  "/dashboard/documents": ["Documents", "Keep your paperwork ready for applications"],
  "/dashboard/my-schemes": ["My Schemes", "Schemes you've applied to"],
  "/dashboard/settings": ["Settings", "Language and notification preferences"],
  "/dashboard/help": ["Help", "Answers and ways to reach us"],
};

const DashboardLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { language, setLanguage } = useLanguage();

  const [langOpen, setLangOpen] = useState(false);

  // /dashboard/scheme/:id has no fixed entry above since the id varies —
  // its own page fetches and shows the real scheme name, so the shared
  // header just uses a generic label here.
  const schemeRouteMatch = location.pathname.match(/^\/dashboard\/scheme\/[^/]+$/);
  let title, subtitle;

  if (schemeRouteMatch) {
    title = "Scheme Details";
    subtitle = "Full scheme information";
  } else {
    [title, subtitle] = HEADER_TEXT[location.pathname] || HEADER_TEXT["/dashboard"];
  }

  function handleLanguageSelect(code) {
    setLanguage(code);
    setLangOpen(false);
    api.updateLanguage(code).catch(() => {
      // Non-fatal — the UI language still switches locally even if the
      // server-side preference update fails (e.g. offline).
    });
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  const navItemClass = ({ isActive }) => `nav-item${isActive ? " active" : ""}`;

  return (
    <div className="dashboard-container">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="sidebar-logo">
          <h1>ESIRE</h1>
          <p>Entrepreneur Scheme Intelligence &amp; Readiness Engine</p>
        </div>

        <nav className="sidebar-nav">

          <div className="nav-section">
            <span className="nav-title">MAIN</span>

            <NavLink to="/dashboard" end className={navItemClass}>
              <span className="nav-icon">⌂</span>
              Dashboard
            </NavLink>

            <NavLink to="/dashboard/profile" className={navItemClass}>
              <span className="nav-icon">◯</span>
              My Profile
            </NavLink>

            <NavLink to="/dashboard/documents" className={navItemClass}>
              <span className="nav-icon">▣</span>
              Documents
            </NavLink>

            <NavLink to="/dashboard/my-schemes" className={navItemClass}>
              <span className="nav-icon">◇</span>
              My Schemes
            </NavLink>
          </div>

          <div className="nav-section secondary">
            <span className="nav-title">OTHER</span>

            <NavLink to="/dashboard/settings" className={navItemClass}>
              <span className="nav-icon">⚙</span>
              Settings
            </NavLink>

            <NavLink to="/dashboard/help" className={navItemClass}>
              <span className="nav-icon">?</span>
              Help
            </NavLink>
          </div>

        </nav>

        <div className="sidebar-logout-wrap">
          <button type="button" className="sidebar-logout-btn" onClick={handleLogout}>
            <span className="nav-icon">⎋</span>
            Logout
          </button>
        </div>

      </aside>

      {/* ================= MAIN CONTENT ================= */}

      <main className="dashboard-main">

        <header className="dashboard-header">
          <div className="header-context">
            <h2>{title}</h2>
            <p>{subtitle}</p>
          </div>

          <div className="header-actions">
            <div className="language-switch">
              <button
                type="button"
                className="language-btn"
                onClick={() => setLangOpen((open) => !open)}
              >
                {languageLabel(language).split(" | ")[0]} ▾
              </button>

              {langOpen && (
                <>
                  <div className="menu-backdrop" onClick={() => setLangOpen(false)} />
                  <div className="language-popover">
                    {LANGUAGE_OPTIONS.map((option) => (
                      <button
                        type="button"
                        key={option.code}
                        className={`language-option${option.code === language ? " selected" : ""}`}
                        onClick={() => handleLanguageSelect(option.code)}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <button className="notification-btn" type="button" aria-label="Notifications">
              ♢
            </button>
          </div>
        </header>

        <div className="dashboard-outlet">
          <Outlet />
        </div>

        <footer className="dashboard-footer">
          <p>© 2026 ESIRE</p>
          <div className="footer-links">
            <button type="button">Privacy</button>
            <Link to="/dashboard/help">Help</Link>
            <button type="button">Contact</button>
          </div>
        </footer>

      </main>

    </div>
  );
};

export default DashboardLayout;
