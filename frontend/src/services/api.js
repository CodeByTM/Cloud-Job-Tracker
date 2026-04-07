import { getToken } from "./auth";

const API_BASE = process.env.REACT_APP_API_BASE_URL;

if (!API_BASE) {
  throw new Error("Missing REACT_APP_API_BASE_URL");
}

function getAuthHeaders() {
  const token = getToken();

  return {
    "Content-Type": "application/json",
    Authorization: token,
  };
}

export async function getDashboard() {
  const response = await fetch(`${API_BASE}/dashboard/`, {
    headers: {
      Authorization: getToken(),
    },
  });

  if (response.status === 429) {
    throw new Error("Too many requests. Please slow down.");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch dashboard");
  }

  return response.json();
}

export async function getJobs() {
  const response = await fetch(`${API_BASE}/jobs`, {
    headers: {
      Authorization: getToken(),
    },
  });

  if (response.status === 429) {
    throw new Error("Too many requests. Please slow down.");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch jobs");
  }

  return response.json();
}

export async function createJob(jobData) {
  const response = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(jobData),
  });

  if (response.status === 429) {
    throw new Error("Too many requests. Please slow down.");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.message || "Failed to create job");
  }

  return response.json();
}

export async function updateJob(jobId, jobData) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(jobData),
  });

  if (response.status === 429) {
    throw new Error("Too many requests. Please slow down.");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.message || "Failed to update job");
  }

  return response.json();
}

export async function deleteJob(jobId) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: "DELETE",
    headers: {
      Authorization: getToken(),
    },
  });

  if (response.status === 429) {
    throw new Error("Too many requests. Please slow down.");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.message || "Failed to delete job");
  }

  return response.json();
}