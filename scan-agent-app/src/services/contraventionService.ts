import { apiService } from './apiService';
import { API_ENDPOINTS } from '../constants/api.constants';
import {
  Contravention,
  ContraventionCreatePayload,
  ContraventionListParams,
} from '../types/contravention.types';

class ContraventionService {
  async listContraventions(params: ContraventionListParams) {
    const config = { params };
    return apiService.get<{ results: Contravention[]; count: number }>(
      API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_LIST,
      config
    );
  }

  async getContravention(id: string) {
    return apiService.get<Contravention>(
      API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_DETAIL(id)
    );
  }

  async createContravention(payload: ContraventionCreatePayload) {
    return apiService.post<Contravention>(
      API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_CREATE,
      payload
    );
  }

  async updateContravention(id: string, updates: Partial<Contravention>) {
    return apiService.put<Contravention>(
      API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_UPDATE(id),
      updates
    );
  }

  async voidContravention(id: string, reason: string) {
    return apiService.post<{ success: boolean }>(
      API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_VOID(id),
      { reason }
    );
  }

  async uploadEvidence(contraventionId: string, file: { uri: string; name: string; type: string }) {
    const formData = new FormData();
    formData.append('file', ({
      uri: file.uri,
      name: file.name,
      type: file.type,
    } as any));

    return apiService.post<{ id: string; url: string }>(
      API_ENDPOINTS.GOVERNMENT_AGENT.EVIDENCE_UPLOAD(contraventionId),
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
  }

  async verifyOffender(identifier: string) {
    return apiService.post<{ exists: boolean; details?: any }>(
      API_ENDPOINTS.GOVERNMENT_AGENT.OFFENDER_VERIFY,
      { identifier }
    );
  }
}

export const contraventionService = new ContraventionService();
