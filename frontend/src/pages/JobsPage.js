import { useState } from "react";

function JobsPage({ jobs, onDelete, onUpdate }) {
  const [editingJobId, setEditingJobId] = useState(null);
  const [editStatus, setEditStatus] = useState("");
  const [editNotes, setEditNotes] = useState("");

  function startEditing(job) {
    setEditingJobId(job.jobId);
    setEditStatus(job.status || "Applied");
    setEditNotes(job.notes || "");
  }

  function cancelEditing() {
    setEditingJobId(null);
    setEditStatus("");
    setEditNotes("");
  }

  async function saveEdit(jobId) {
    await onUpdate(jobId, {
      status: editStatus,
      notes: editNotes,
    });
    cancelEditing();
  }

  return (
    <section>
      <h2>Job Applications</h2>

      {jobs.length === 0 ? (
        <p>No job applications yet.</p>
      ) : (
        <div className="jobs-list">
          {jobs.map((job) => (
            <div className="job-card" key={job.jobId}>
              <h3>{job.title}</h3>
              <p><strong>Company:</strong> {job.company}</p>
              <p><strong>Date Applied:</strong> {job.dateApplied}</p>
              <p><strong>Location:</strong> {job.location || "N/A"}</p>

              {editingJobId === job.jobId ? (
                <>
                  <label>Status</label>
                  <select
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                  >
                    <option value="Applied">Applied</option>
                    <option value="Interviewing">Interviewing</option>
                    <option value="Rejected">Rejected</option>
                    <option value="Offer">Offer</option>
                    <option value="Accepted">Accepted</option>
                  </select>

                  <label>Notes</label>
                  <textarea
                    rows="4"
                    value={editNotes}
                    onChange={(e) => setEditNotes(e.target.value)}
                  />

                  <div className="job-actions">
                    <button onClick={() => saveEdit(job.jobId)}>Save</button>
                    <button onClick={cancelEditing}>Cancel</button>
                  </div>
                </>
              ) : (
                <>
                  <p>
                  <strong>Status:</strong>{" "}
                  <span className={`status ${job.status.toLowerCase()}`}>
                  {job.status}
                  </span>
                  </p>
                  <p><strong>Notes:</strong> {job.notes || "None"}</p>

                  {job.jobUrl && (
                    <p>
                      <strong>Link:</strong>{" "}
                      <a href={job.jobUrl} target="_blank" rel="noreferrer">
                        View Posting
                      </a>
                    </p>
                  )}

                  <div className="job-actions">
                    <button onClick={() => startEditing(job)}>Edit</button>
                    <button onClick={() => onDelete(job.jobId)}>Delete</button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default JobsPage;