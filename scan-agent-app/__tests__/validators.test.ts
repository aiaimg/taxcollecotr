// Simple validator functions for testing
const validateBadgeId = (badgeId: string): boolean => {
  const badgeIdPattern = /^AGT\d{6}$/;
  return badgeIdPattern.test(badgeId);
};

const validatePIN = (pin: string): boolean => {
  const pinPattern = /^\d{6}$/;
  return pinPattern.test(pin);
};

const validateLicensePlate = (plate: string): boolean => {
  const platePattern = /^[A-Z]{2,3}\d{3,4}[A-Z]{0,2}$/;
  return platePattern.test(plate);
};

describe('Validators', () => {
  describe('validateBadgeId', () => {
    it('should validate correct badge IDs', () => {
      expect(validateBadgeId('AGT123456')).toBe(true);
      expect(validateBadgeId('AGT000001')).toBe(true);
    });

    it('should reject invalid badge IDs', () => {
      expect(validateBadgeId('')).toBe(false);
      expect(validateBadgeId('AGT123')).toBe(false);
      expect(validateBadgeId('AGT1234567')).toBe(false);
      expect(validateBadgeId('INVALID')).toBe(false);
    });
  });

  describe('validatePIN', () => {
    it('should validate correct PINs', () => {
      expect(validatePIN('123456')).toBe(true);
      expect(validatePIN('000000')).toBe(true);
      expect(validatePIN('999999')).toBe(true);
    });

    it('should reject invalid PINs', () => {
      expect(validatePIN('')).toBe(false);
      expect(validatePIN('12345')).toBe(false);
      expect(validatePIN('1234567')).toBe(false);
      expect(validatePIN('ABCDEF')).toBe(false);
    });
  });

  describe('validateLicensePlate', () => {
    it('should validate correct license plates', () => {
      expect(validateLicensePlate('AB123CD')).toBe(true);
      expect(validateLicensePlate('ABC1234')).toBe(true);
      expect(validateLicensePlate('AB1234C')).toBe(true);
    });

    it('should reject invalid license plates', () => {
      expect(validateLicensePlate('')).toBe(false);
      expect(validateLicensePlate('INVALID')).toBe(false);
      expect(validateLicensePlate('123ABC')).toBe(false);
    });
  });
});