import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Agent, AgentType, LoginCredentials, AuthResponse } from '../types/auth.types';
import { authService } from '../services/authService';
import { storageService } from '../services/storageService';

interface AuthContextType {
  agent: Agent | null;
  agentType: AgentType | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  canAccessFeature: (feature: string) => boolean;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [agentType, setAgentType] = useState<AgentType | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      const token = await storageService.getAuthToken();
      
      if (token) {
        const profile = await authService.getProfile();
        if (profile) {
          setAgent(profile);
          setAgentType(profile.type);
        } else {
          // Token is invalid, clear it
          await storageService.clearAuthData();
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      await storageService.clearAuthData();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await authService.login(credentials);
      
      if (response.success && response.agent) {
        setAgent(response.agent);
        setAgentType(response.agent.type);
        
        // Store auth token
        if (response.token) {
          await storageService.setAuthToken(response.token);
        }
        if (response.refreshToken) {
          await storageService.setRefreshToken(response.refreshToken);
        }
        
        // Store agent profile
        await storageService.setAgentProfile(response.agent);
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local data regardless of server response
      await storageService.clearAuthData();
      setAgent(null);
      setAgentType(null);
      setIsLoading(false);
    }
  };

  const hasPermission = (permission: string): boolean => {
    if (!agent || !agentType) {
      return false;
    }
    
    // Check if agent has the specific permission
    return agent.permissions.includes(permission);
  };

  const canAccessFeature = (feature: string): boolean => {
    if (!agent || !agentType) {
      return false;
    }
    
    // Map features to required permissions
    const featurePermissions: Record<string, string[]> = {
      'scanner': ['scan_qr', 'scan_barcode', 'scan_license_plate'],
      'payments': ['process_payment'],
      'history': ['view_history', 'view_payment_history'],
      'statistics': ['view_statistics'],
      'commissions': ['view_commissions'],
      'cash_session': ['manage_cash_session'],
      'receipts': ['generate_receipt'],
      'contraventions': ['view_contraventions', 'issue_contravention', 'process_contraventions'],
    };
    
    const requiredPermissions = featurePermissions[feature] || [];
    
    // Check if agent has any of the required permissions
    return requiredPermissions.some(permission => agent.permissions.includes(permission));
  };

  const refreshProfile = async (): Promise<void> => {
    try {
      const profile = await authService.getProfile();
      if (profile) {
        setAgent(profile);
        setAgentType(profile.type);
        await storageService.setAgentProfile(profile);
      }
    } catch (error) {
      console.error('Error refreshing profile:', error);
    }
  };

  const value: AuthContextType = {
    agent,
    agentType,
    isAuthenticated: !!agent && !!agentType,
    isLoading,
    login,
    logout,
    hasPermission,
    canAccessFeature,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
