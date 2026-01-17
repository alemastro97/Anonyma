// API Types for Anonyma

export interface AnonymizeTextRequest {
  text: string;
  mode: 'redact' | 'substitute' | 'visual_redact';
  language?: string;
  use_flair?: boolean;
}

export interface Detection {
  text: string;
  entity_type: string;
  start: number;
  end: number;
  confidence: number;
}

export interface AnonymizeTextResponse {
  success: boolean;
  anonymized_text: string;
  detections_count: number;
  detections: Detection[];
  processing_time: number;
  error?: string;
}

export interface ProcessDocumentResponse {
  success: boolean;
  job_id: string;
  format?: string;
  detections_count: number;
  processing_time: number;
  download_url?: string;
  error?: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result?: {
    format: string;
    detections_count: number;
    processing_time: number;
    output_file: string;
    original_file: string;
  };
  error?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  engines_loaded: {
    basic: boolean;
    flair: boolean;
  };
}

export interface ConfigResponse {
  features: {
    redis_enabled: boolean;
    auth_enabled: boolean;
    rate_limit_enabled: boolean;
  };
  limits: {
    max_file_size: number;
    rate_limit_requests: number | null;
    rate_limit_window: number | null;
  };
  version: string;
}
