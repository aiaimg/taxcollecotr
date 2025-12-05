import { apiService } from './apiService';
import { storageService } from './storageService';
import { API_ENDPOINTS } from '../constants/api.constants';

interface AuditLogItem {
  id: string;
  type: string;
  actorId: string;
  resourceId?: string;
  details?: Record<string, any>;
  timestamp: string;
}

class AuditService {
  async logAction(type: string, actorId: string, resourceId: string | undefined, details?: Record<string, any>) {
    const item: AuditLogItem = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type,
      actorId,
      resourceId,
      details,
      timestamp: new Date().toISOString(),
    };

    try {
      const endpoint = '/audit/logs/';
      const res = await apiService.post(endpoint, item);
      if (!res.success) {
        await storageService.addToOfflineQueue({ ...item, kind: 'audit' });
      }
    } catch (e) {
      await storageService.addToOfflineQueue({ ...item, kind: 'audit' });
    }
  }

  async syncOfflineLogs() {
    const queue = await storageService.getOfflineQueue();
    const auditItems = queue.filter(i => i.kind === 'audit');
    for (const item of auditItems) {
      try {
        const endpoint = '/audit/logs/';
        const res = await apiService.post(endpoint, item);
        if (res.success) {
          await storageService.removeFromOfflineQueue(item.id);
        }
      } catch (e) {}
    }
  }

  async purgeOldAuditLogs(retentionMs: number = 24 * 60 * 60 * 1000) {
    const now = Date.now();
    const queue = await storageService.getOfflineQueue();
    const kept = queue.filter(i => {
      if (i.kind !== 'audit') return true;
      const ts = new Date(i.timestamp).getTime();
      return now - ts <= retentionMs;
    });
    if (kept.length !== queue.length) {
      await storageService.setOfflineQueue(kept);
    }
  }
}

export const auditService = new AuditService();
