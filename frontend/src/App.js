import { useEffect, useState } from "react";
import { createJob, deleteJob, getDashboard, getJobs, updateJob } from "./services/api";
import { getCurrentEmail, isAuthenticated, signOut } from "./services/auth";
import DashboardPage from "./pages/DashboardPage";
import JobsPage from "./pages/JobsPage";
import JobForm from "./components/JobForm";
import AuthForm from "./components/AuthForm";
import "./styles.css";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [email, setEmail] = useState(getCurrentEmail());
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  async function loadData() {
    try {
      setLoading(true);
      setError("");

      const dashboardData = await getDashboard();
      const jobsData = await getJobs();

      setDashboard(dashboardData.dashboard);
      setJobs(jobsData.jobs || []);
    } catch (err) {
      setError("Failed to load data from API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    if (authenticated) {
      loadData();
    }
  }, [authenticated]);

  async function handleCreateJob(jobData) {
    await createJob(jobData);
    await loadData();
  }

  async function handleDeleteJob(jobId) {
    await deleteJob(jobId);
    await loadData();
  }

  async function handleUpdateJob(jobId, updates) {
    await updateJob(jobId, updates);
    await loadData();
  }

  function handleAuthSuccess() {
    setAuthenticated(true);
    setEmail(getCurrentEmail());
  }

  function handleLogout() {
    signOut();
    setAuthenticated(false);
    setEmail("");
    setJobs([]);
    setDashboard(null);
  }

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  if (!authenticated) {
    return (
      <div className="container">
        <div className="top-bar auth-top-bar">
          <h1>Cloud Job Tracker</h1>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === "light" ? "Dark Mode" : "Light Mode"}
          </button>
        </div>
        <AuthForm onAuthSuccess={handleAuthSuccess} />
      </div>
    );
  }

  return (
    <div className="container">
      <div className="top-bar">
        <h1>Cloud Job Tracker</h1>
        <div className="user-box">
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === "light" ? "Dark Mode" : "Light Mode"}
          </button>
          <span>{email}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <DashboardPage dashboard={dashboard} />
      <JobForm onJobCreated={handleCreateJob} />
      <JobsPage jobs={jobs} onDelete={handleDeleteJob} onUpdate={handleUpdateJob} />
    </div>
  );
}

export default App;