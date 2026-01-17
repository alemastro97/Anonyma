import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  AnonymizeTextRequest,
  AnonymizeTextResponse,
  ProcessDocumentResponse,
  JobStatusResponse,
  HealthResponse,
  ConfigResponse,
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || '';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for long-running operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add API key to requests if configured
if (API_KEY) {
  apiClient.defaults.headers.common['X-API-Key'] = API_KEY;
}

// Add JWT token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('anonyma_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const data: any = error.response.data;

      if (status === 401) {
        throw new Error('Authentication required. Please provide a valid API key.');
      } else if (status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      } else if (status === 413) {
        throw new Error('File too large. Please upload a smaller file.');
      } else if (data?.detail) {
        throw new Error(data.detail);
      } else {
        throw new Error(`API Error: ${status}`);
      }
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred.');
    }
  }
);

// API Service
export const anonymaApi = {
  /**
   * Health check
   */
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  /**
   * Get API configuration
   */
  config: async (): Promise<ConfigResponse> => {
    const response = await apiClient.get<ConfigResponse>('/api/config');
    return response.data;
  },

  /**
   * Anonymize text
   */
  anonymizeText: async (
    request: AnonymizeTextRequest
  ): Promise<AnonymizeTextResponse> => {
    const response = await apiClient.post<AnonymizeTextResponse>(
      '/anonymize/text',
      request
    );
    return response.data;
  },

  /**
   * Anonymize document (upload file)
   */
  anonymizeDocument: async (
    file: File,
    mode: string = 'redact',
    language: string = 'it',
    useFlair: boolean = false
  ): Promise<ProcessDocumentResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ProcessDocumentResponse>(
      `/anonymize/document?mode=${mode}&language=${language}&use_flair=${useFlair}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Get job status
   */
  getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
    const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);
    return response.data;
  },

  /**
   * Download anonymized document
   */
  downloadDocument: async (jobId: string): Promise<Blob> => {
    const response = await apiClient.get(`/jobs/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Get supported formats
   */
  getSupportedFormats: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/formats');
    return response.data;
  },

  /**
   * Set API key for authenticated requests
   */
  setApiKey: (key: string) => {
    if (key) {
      apiClient.defaults.headers.common['X-API-Key'] = key;
    } else {
      delete apiClient.defaults.headers.common['X-API-Key'];
    }
  },
};

export default anonymaApi;
