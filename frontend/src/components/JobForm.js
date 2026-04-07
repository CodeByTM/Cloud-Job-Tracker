import { useState } from "react";

function JobForm({ onJobCreated }) {
  const [formData, setFormData] = useState({
    company: "",
    title: "",
    status: "Applied",
    dateApplied: "",
    location: "",
    jobUrl: "",
    notes: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function validateForm(data) {
    if (!data.company.trim()) return "Company is required";
    if (!data.title.trim()) return "Job title is required";
    if (!data.dateApplied.trim()) return "Date is required";

    if (data.jobUrl && !data.jobUrl.startsWith("http")) {
      return "Job URL must start with http or https";
    }

    return null;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    // 🔒 Clean + sanitize inputs (frontend layer)
    const cleanedData = {
      company: formData.company.trim(),
      title: formData.title.trim(),
      status: formData.status.trim(),
      dateApplied: formData.dateApplied.trim(),
      location: formData.location.trim(),
      jobUrl: formData.jobUrl.trim(),
      notes: formData.notes.trim(),
    };

    // 🔒 Basic validation
    const validationError = validateForm(cleanedData);
    if (validationError) {
      setError(validationError);
      setLoading(false);
      return;
    }

    try {
      await onJobCreated(cleanedData);

      setFormData({
        company: "",
        title: "",
        status: "Applied",
        dateApplied: "",
        location: "",
        jobUrl: "",
        notes: "",
      });
    } catch (err) {
      setError("Could not create job.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="job-form" onSubmit={handleSubmit}>
      <h2>Add Job</h2>

      <input
        type="text"
        name="company"
        placeholder="Company"
        value={formData.company}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="title"
        placeholder="Job Title"
        value={formData.title}
        onChange={handleChange}
        required
      />

      <select name="status" value={formData.status} onChange={handleChange}>
        <option value="Applied">Applied</option>
        <option value="Interviewing">Interviewing</option>
        <option value="Rejected">Rejected</option>
        <option value="Offer">Offer</option>
        <option value="Accepted">Accepted</option>
      </select>

      <input
        type="date"
        name="dateApplied"
        value={formData.dateApplied}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="location"
        placeholder="Location"
        value={formData.location}
        onChange={handleChange}
      />

      <input
        type="url"
        name="jobUrl"
        placeholder="Job URL"
        value={formData.jobUrl}
        onChange={handleChange}
      />

      <textarea
        name="notes"
        placeholder="Notes"
        value={formData.notes}
        onChange={handleChange}
        rows="4"
      />

      <button type="submit" disabled={loading}>
        {loading ? "Saving..." : "Add Job"}
      </button>

      {error && <p className="error">{error}</p>}
    </form>
  );
}

export default JobForm;