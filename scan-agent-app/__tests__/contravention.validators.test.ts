import { validateOffenseDetails, validateEvidenceUri, validateCoordinates } from '../src/utils/validators';

describe('contravention validators', () => {
  test('validateOffenseDetails rejects short or empty', () => {
    expect(validateOffenseDetails('')).toBe(false);
    expect(validateOffenseDetails('abc')).toBe(false);
  });

  test('validateOffenseDetails accepts reasonable length', () => {
    expect(validateOffenseDetails('Parking in a no-parking zone')).toBe(true);
  });

  test('validateEvidenceUri accepts http/file/content schemes', () => {
    expect(validateEvidenceUri('http://example.com/photo.jpg')).toBe(true);
    expect(validateEvidenceUri('file:///var/mobile/evidence.jpg')).toBe(true);
    expect(validateEvidenceUri('content://media/external/images/media/1')).toBe(true);
  });

  test('validateEvidenceUri rejects invalid', () => {
    expect(validateEvidenceUri('not a uri')).toBe(false);
  });

  test('validateCoordinates within Madagascar bounds', () => {
    expect(validateCoordinates(-18.9, 47.5)).toBe(true);
    expect(validateCoordinates(0, 0)).toBe(false);
  });
});

