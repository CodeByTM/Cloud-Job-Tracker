function DashboardPage({ dashboard }) {
  const stats = dashboard || {
    total: 0,
    applied: 0,
    interviewing: 0,
    rejected: 0,
    offer: 0,
    accepted: 0,
  };

  return (
    <section>
      <h2>Dashboard</h2>
      <div className="dashboard-grid">
        <div className="card">
          <h3>Total</h3>
          <p>{stats.total}</p>
        </div>
        <div className="card">
          <h3>Applied</h3>
          <p>{stats.applied}</p>
        </div>
        <div className="card">
          <h3>Interviewing</h3>
          <p>{stats.interviewing}</p>
        </div>
        <div className="card">
          <h3>Rejected</h3>
          <p>{stats.rejected}</p>
        </div>
        <div className="card">
          <h3>Offer</h3>
          <p>{stats.offer}</p>
        </div>
        <div className="card">
          <h3>Accepted</h3>
          <p>{stats.accepted}</p>
        </div>
      </div>
    </section>
  );
}

export default DashboardPage;