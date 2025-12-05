import { Agent, LoginCredentials, AuthResponse } from '../types/auth.types';
import { API_ENDPOINTS, API_BASE_URL } from '../constants/api.constants';
import { apiService } from './apiService';
import { storageService } from './storageService';
import { t } from '../utils/translations';

class AuthService {
  private currentAgent: Agent | null = null;

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
      
      if (response.success && response.data) {
        const tokens = response.data;
        const token = tokens.access;
        const refreshToken = tokens.refresh;

        // Store tokens temporarily so profile requests include Authorization header
        if (token) {
          await storageService.setAuthToken(token);
        }
        if (refreshToken) {
          await storageService.setRefreshToken(refreshToken);
        }

        // Fetch agent profile after successful login
        const agentProfile = await this.getProfile();

        return {
          success: true,
          token,
          refreshToken,
          agent: agentProfile || undefined,
        };
      }

      return {
        success: false,
        error: response.error || t('login.loginFailed'),
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : t('login.loginFailed'),
      };
    }
  }

  async logout(): Promise<void> {
    try {
      await apiService.post(API_ENDPOINTS.AUTH.LOGOUT, {});
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with logout even if API call fails
    } finally {
      this.currentAgent = null;
    }
  }

  async getProfile(): Promise<Agent | null> {
    try {
      // Try government profile first
      let response = await apiService.get(API_ENDPOINTS.GOVERNMENT_AGENT.PROFILE);
      if (response.success && response.data) {
        const agentData = response.data;
        const agent: Agent = {
          id: String(agentData.id || agentData.agent_id || ''),
          badgeId: String(agentData.numero_badge || agentData.badge_id || ''),
          type: 'agent_government' as any,
          name: String(agentData.nom_complet || agentData.name || ''),
          permissions: [],
          region: String(agentData.zone_affectation || agentData.region || ''),
          department: String(agentData.service || agentData.department || ''),
          isActive: Boolean(agentData.est_actif ?? true),
          email: agentData.email,
          phone: agentData.telephone,
          createdAt: new Date(),
          lastLogin: undefined,
        };
        this.currentAgent = agent;
        return agent;
      }

      // Fallback to partner profile
      response = await apiService.get(API_ENDPOINTS.PARTNER_AGENT.PROFILE);
      if (response.success && response.data) {
        const agentData = response.data;
        const agent: Agent = {
          id: String(agentData.id || agentData.agent_id || ''),
          badgeId: String(agentData.agent_id || ''),
          type: 'agent_partenaire' as any,
          name: String(agentData.user_name || agentData.name || ''),
          permissions: [],
          region: String(agentData.zone_affectation || agentData.region || ''),
          department: String(agentData.service || agentData.department || ''),
          isActive: true,
          email: agentData.email,
          phone: agentData.telephone,
          createdAt: new Date(),
          lastLogin: undefined,
        };
        this.currentAgent = agent;
        return agent;
      }

      return null;
    } catch (error) {
      console.error('Get profile error:', error);
      return null;
    }
  }

  async refreshToken(): Promise<string | null> {
    try {
      const response = await apiService.post(API_ENDPOINTS.AUTH.REFRESH, {});
      
      if (response.success && response.data?.access) {
        return response.data.access;
      }

      return null;
    } catch (error) {
      console.error('Refresh token error:', error);
      return null;
    }
  }

  getCurrentAgent(): Agent | null {
    return this.currentAgent;
  }

  isAuthenticated(): boolean {
    return this.currentAgent !== null;
  }

  hasPermission(permission: string): boolean {
    if (!this.currentAgent) {
      return false;
    }
    return this.currentAgent.permissions.includes(permission);
  }

  getAgentType(): string | null {
    return this.currentAgent?.type || null;
  }

  canAccessEndpoint(endpoint: string): boolean {
    if (!this.currentAgent) {
      return false;
    }

    // Map endpoints to required permissions
    const endpointPermissions: Record<string, string[]> = {
      [API_ENDPOINTS.GOVERNMENT_AGENT.VERIFY_QR]: ['scan_qr', 'verify_code'],
      [API_ENDPOINTS.GOVERNMENT_AGENT.SCAN_HISTORY]: ['view_history'],
      [API_ENDPOINTS.GOVERNMENT_AGENT.STATISTICS]: ['view_statistics'],
      [API_ENDPOINTS.GOVERNMENT_AGENT.VEHICLE_INFO]: ['scan_license_plate'],
      [API_ENDPOINTS.GOVERNMENT_AGENT.CONTRAVENTIONS_LIST]: ['view_contraventions'],
      // Dynamic endpoints are mapped by prefix checks below
      [API_ENDPOINTS.PARTNER_AGENT.PROCESS_PAYMENT]: ['process_payment'],
      [API_ENDPOINTS.PARTNER_AGENT.MY_SESSIONS]: ['manage_cash_session'],
      [API_ENDPOINTS.PARTNER_AGENT.GENERATE_RECEIPT]: ['generate_receipt'],
      [API_ENDPOINTS.PARTNER_AGENT.COMMISSIONS]: ['view_commissions'],
    };

    const requiredPermissions = endpointPermissions[endpoint] || [];
    if (requiredPermissions.length) {
      return requiredPermissions.some(permission => this.hasPermission(permission));
    }

    // Handle dynamic government contravention endpoints
    if (endpoint.startsWith('/agent-government/contraventions/')) {
      // detail/update/void/evidence map to processing permissions
      const needsProcessing = endpoint.includes('/update/') || endpoint.includes('/void/') || endpoint.includes('/evidence/');
      const needsCreate = endpoint.endsWith('/create/');
      if (needsCreate) return this.hasPermission('issue_contravention');
      if (needsProcessing) return this.hasPermission('process_contraventions') || this.hasPermission('void_contravention');
      return this.hasPermission('view_contraventions');
    }

    return false;
  }
}

export const authService = new AuthService();
