// Simple formatter functions for testing
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const formatBadgeId = (badgeId: string): string => {
  return badgeId.toUpperCase();
};

describe('Formatters', () => {
  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1500000)).toBe('$1,500,000.00');
      expect(formatCurrency(0)).toBe('$0.00');
    });
  });

  describe('formatDate', () => {
    it('should format dates correctly', () => {
      const date = new Date('2024-01-15T10:30:00');
      expect(formatDate(date)).toBe('Jan 15, 2024, 10:30 AM');
    });
  });

  describe('formatBadgeId', () => {
    it('should format badge IDs correctly', () => {
      expect(formatBadgeId('AGT123456')).toBe('AGT123456');
      expect(formatBadgeId('AGT000001')).toBe('AGT000001');
    });
  });
});