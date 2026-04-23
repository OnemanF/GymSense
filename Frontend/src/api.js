import axios from "axios";

// for deployment use https://github.com/OnemanF/GymSense.git
const API_BASE_URL = "http://127.0.0.1:8000";

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