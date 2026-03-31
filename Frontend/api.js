import { getAuthToken } from "./src/lib/auth";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";
const USE_MOCK_API = String(import.meta.env.VITE_USE_MOCK_API || "false") === "true";

async function buildAuthHeaders(base = {}) {
  const token = await getAuthToken();
  if (!token) return base;
  return {
    ...base,
    Authorization: `Bearer ${token}`,
  };
}

/**
 * Generic API fetch wrapper with timeout and error handling
 * @param {string} endpoint - API endpoint path (e.g., "/api/upload")
 * @param {Object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<Object>} Parsed JSON response
 */
async function apiFetch(endpoint, options = {}) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000); // 45 seconds timeout

    const headers = await buildAuthHeaders(options.headers || {});
    
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }

    if (!res.ok) {
      const errorMessage = data.message || data.error || `Server responded with status ${res.status}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (err) {
    console.error("API request failed:", err);
    if (err.name === 'AbortError') {
      throw new Error("Request timed out. Server might be slow or offline.");
    }
    throw err;
  }
}

/**
 * Upload image or video file for deepfake detection
 * @param {File} file - The file selected by user
 * @returns {Promise<Object>} Prediction result
 */
export async function uploadFile(file) {
  if (!file) {
    throw new Error("No file selected");
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const result = await apiFetch("/api/upload", {
      method: "POST",
      body: formData,
      // Do NOT set Content-Type – browser sets it automatically with boundary for FormData
    });

    // Expected successful response shape
    if (!result.prediction) {
      throw new Error("Invalid response format from server");
    }

    return result;
  } catch (err) {
    console.error("Upload failed:", err);
    if (USE_MOCK_API) {
      console.warn("Upload to backend failed, falling back to mock response:", err);
      return mockUploadResponse();
    }
    throw new Error(
      err.message.includes("Analysis failed")
        ? "Deepfake analysis failed on server. Please check if model file exists."
        : err.message
    );
  }
}

// Legacy alias for backward compatibility
export const uploadImage = uploadFile;

export async function fetchModelInfo() {
  try {
    const result = await apiFetch("/api/model-info");
    return result;
  } catch (error) {
    console.warn("Fetching model info failed:", error);
    return {
      status: "not_loaded",
      message: "Model information unavailable"
    };
  }
}

export async function fetchDetectionLogs(params = {}) {
  try {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") return;
      query.set(key, String(value));
    });

    const url = query.toString() ? `/api/logs?${query.toString()}` : "/api/logs";
    const data = await apiFetch(url);

    if (Array.isArray(data)) {
      return {
        items: data,
        total: data.length,
        page: 1,
        page_size: data.length,
      };
    }
    return data;
  } catch (error) {
    if (USE_MOCK_API) {
      console.warn("Fetching detection logs failed, falling back to mock logs:", error);
      const items = mockLogsResponse();
      return {
        items,
        total: items.length,
        page: 1,
        page_size: items.length,
      };
    }
    throw error;
  }
}

export async function deleteDetectionLog(logId) {
  const data = await apiFetch(`/api/logs/${encodeURIComponent(logId)}`, {
    method: "DELETE",
  });
  return data;
}

export async function clearDetectionLogs(sourceType = "") {
  const query = sourceType ? `?source_type=${encodeURIComponent(sourceType)}` : "";
  const data = await apiFetch(`/api/logs${query}`, {
    method: "DELETE",
  });
  return data;
}

export async function logLiveEvent(payload) {
  const data = await apiFetch("/api/live-events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
  return data;
}

export async function fetchStats() {
  try {
    const data = await apiFetch("/api/stats");
    return data;
  } catch (error) {
    console.warn("Fetching stats failed, using empty defaults:", error);
    return null;
  }
}

function mockUploadResponse() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const isFake = Math.random() > 0.5;
      const confidence = 70 + Math.random() * 30;
      
      resolve({
        prediction: isFake ? "Fake" : "Real",
        confidence: confidence,
        filename: "mock_upload.jpg",
        isVideo: false,
        threat_level: confidence > 80 ? "high" : confidence > 50 ? "medium" : "low",
        model_used: "Mock Model (Backend Unavailable)",
        processing_time: {
          preprocessing_ms: 10 + Math.random() * 20,
          inference_ms: 50 + Math.random() * 100,
          total_ms: 60 + Math.random() * 120
        },
        analysis: {
          level: "Mock",
          description: "Backend unavailable. Using mock prediction.",
          recommendation: "Please ensure backend server is running for accurate results."
        },
        model_info: {
          architecture: "N/A",
          input_size: "N/A",
          framework: "Mock",
          device: "cpu"
        }
      });
    }, 800);
  });
}

function mockLogsResponse() {
  const now = new Date();
  const entries = [];

  for (let i = 0; i < 12; i++) {
    const ts = new Date(now.getTime() - i * 5 * 60_000).toISOString();
    const isFake = Math.random() > 0.6;
    const confidence = 0.6 + Math.random() * 0.35;

    entries.push({
      timestamp: ts,
      filename: `mock_upload_${String(i + 1).padStart(3, "0")}.jpg`,
      prediction: isFake ? "Fake" : "Real",
      confidence,
    });
  }

  return entries;
}
