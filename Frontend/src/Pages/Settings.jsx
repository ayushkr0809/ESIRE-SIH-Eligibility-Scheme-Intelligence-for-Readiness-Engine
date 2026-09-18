import { useState } from "react";
import { LANGUAGE_OPTIONS } from "../Components/languages";
import { useLanguage } from "../i18n/LanguageContext";
import { api } from "../api/client";
import "./Settings.css";

function Settings() {
  const { language, setLanguage } = useLanguage();
  const [pendingLanguage, setPendingLanguage] = useState(language);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(true);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  function handleLanguageChange(e) {
    setPendingLanguage(e.target.value);
    setSaved(false);
  }

  async function handleSave() {
    setError("");
    setLanguage(pendingLanguage);
    try {
      await api.updateLanguage(pendingLanguage);
      setSaved(true);
    } catch (err) {
      setError(err.message || "Saved locally, but couldn't sync to your account.");
    }
  }

  return (
    <section className="settings-page">

      <div className="dashboard-title">
        <h1>Settings</h1>
        <p>Language and notification preferences</p>
      </div>

      <div className="settings-card">

        <div className="settings-row">
          <div>
            <h3>Preferred language</h3>
            <p>Used across the dashboard and for scheme recommendations.</p>
          </div>
          <select value={pendingLanguage} onChange={handleLanguageChange} className="settings-select">
            {LANGUAGE_OPTIONS.map((lang) => (
              <option key={lang.code} value={lang.code}>{lang.label}</option>
            ))}
          </select>
        </div>

        <div className="settings-row">
          <div>
            <h3>Email notifications</h3>
            <p>New scheme matches and application updates.</p>
          </div>
          <button
            type="button"
            className={`settings-toggle${emailAlerts ? " on" : ""}`}
            onClick={() => { setEmailAlerts((v) => !v); setSaved(false); }}
            aria-pressed={emailAlerts}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <div className="settings-row">
          <div>
            <h3>SMS notifications</h3>
            <p>Deadline reminders for schemes you've applied to.</p>
          </div>
          <button
            type="button"
            className={`settings-toggle${smsAlerts ? " on" : ""}`}
            onClick={() => { setSmsAlerts((v) => !v); setSaved(false); }}
            aria-pressed={smsAlerts}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <div className="settings-actions">
          <button type="button" className="settings-save" onClick={handleSave}>
            Save changes
          </button>
          {saved && <span className="settings-saved-note">Saved</span>}
          {error && <span className="settings-saved-note" style={{ color: "#b3261e" }}>{error}</span>}
        </div>

      </div>

    </section>
  );
}

export default Settings;
