import { getToken } from "./auth";

const API_BASE = "https://er4985kgm0.execute-api.us-east-1.amazonaws.com/Prod";

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

  if (!response.ok) {
    throw new Error("Failed to create job");
  }

  return response.json();
}

export async function updateJob(jobId, jobData) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(jobData),
  });

  if (!response.ok) {
    throw new Error("Failed to update job");
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

  if (!response.ok) {
    throw new Error("Failed to delete job");
  }

  return response.json();
}