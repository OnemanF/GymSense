import axios from "axios";

// for deployment use https://github.com/OnemanF/GymSense.git
//const API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = "https://gymsense.onrender.com";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function fetchLatestMeasurement() {
  const response = await api.get("/api/measurements/latest");
  return response.data;
}

export async function fetchMeasurementHistory(limit = 20) {
  const response = await api.get(`/api/measurements/history?limit=${limit}`);
  return response.data;
}

export async function fetchMeasurementSummary(hours = 24) {
  const response = await api.get(`/api/measurements/summary?hours=${hours}`);
  return response.data;
}

export async function fetchCurrentAssessment() {
  const response = await api.get("/api/ai/current-assessment");
  return response.data;
}

export async function fetchGymAgentAssessment() {
  const response = await api.get("/api/ai/gym-agent-assessment");
  return response.data;
}