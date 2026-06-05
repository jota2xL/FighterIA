import apiClient from "./api.client";
import type { Certificate, CertificateVerifyResponse } from "@/types/blockchain.types";

export const blockchainService = {
  generateCertificate: (analysisId: number) =>
    apiClient
      .post<Certificate>(`/blockchain/certificates/generate/${analysisId}`)
      .then((r) => r.data),

  verifyCertificate: (hash: string) =>
    apiClient
      .get<CertificateVerifyResponse>(`/blockchain/certificates/${hash}`)
      .then((r) => r.data),
};
