jest.mock('../src/services/apiService', () => {
  return {
    apiService: {
      get: jest.fn(async () => ({ success: true, data: { id: '1' }, timestamp: new Date().toISOString() })),
      post: jest.fn(async () => ({ success: true, data: { id: '1' }, timestamp: new Date().toISOString() })),
      put: jest.fn(async () => ({ success: true, data: { id: '1' }, timestamp: new Date().toISOString() })),
    },
  };
});

import { contraventionService } from '../src/services/contraventionService';

describe('contraventionService', () => {
  test('createContravention returns success', async () => {
    const res = await contraventionService.createContravention({
      offenderId: 'ABC123',
      offenseDetails: 'Parking violation',
      location: { latitude: -18.9, longitude: 47.5 },
      timestamp: new Date().toISOString(),
    });
    expect(res.success).toBe(true);
    expect(res.data?.id).toBe('1');
  });

  test('listContraventions returns results', async () => {
    const res = await contraventionService.listContraventions({ page: 1, pageSize: 10 });
    expect(res.success).toBe(true);
  });
});

