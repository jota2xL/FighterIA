export interface Certificate {
  id: number;
  analysis_id: number;
  hash: string;
  issued_at: string;
  verified_count: number;
}

export interface CertificateVerifyResponse {
  valid: boolean;
  certificate: Certificate | null;
  message: string;
}
