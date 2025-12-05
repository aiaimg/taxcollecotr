import { t, setLanguage, getLanguage } from '../src/utils/translations';

describe('Translation System', () => {
  beforeEach(() => {
    // Reset to French before each test
    setLanguage('fr');
  });

  describe('French translations', () => {
    it('should translate basic keys', () => {
      expect(t('common.valid')).toBe('Valide');
      expect(t('common.invalid')).toBe('Invalide');
      expect(t('common.paid')).toBe('Payé');
      expect(t('common.pending')).toBe('En attente');
      expect(t('common.yes')).toBe('Oui');
      expect(t('common.no')).toBe('Non');
      expect(t('common.close')).toBe('Fermer');
    });

    it('should translate login screen', () => {
      expect(t('login.title')).toBe('Agent de collecte des taxes');
      expect(t('login.loginButton')).toBe('Se connecter');
      expect(t('login.badgeId')).toBe('ID de badge');
    });

    it('should translate dashboard', () => {
      expect(t('dashboard.scan')).toBe('Scanner');
      expect(t('dashboard.history')).toBe('Historique');
      expect(t('dashboard.profile')).toBe('Profil');
    });

    it('should handle parameterized strings', () => {
      expect(t('history.totalScans', { count: 5 })).toBe('5 scans au total');
    });
  });

  describe('Malagasy translations', () => {
    beforeEach(() => {
      setLanguage('mg');
    });

    it('should translate basic keys', () => {
      expect(t('common.valid')).toBe('Mety');
      expect(t('common.invalid')).toBe('Tsy mety');
      expect(t('common.paid')).toBe('Voaloa');
      expect(t('common.pending')).toBe('Miandry');
      expect(t('common.yes')).toBe('Eny');
      expect(t('common.no')).toBe('Tsia');
      expect(t('common.close')).toBe('Atsahatra');
    });

    it('should translate login screen', () => {
      expect(t('login.title')).toBe('Mpangataka hetra');
      expect(t('login.loginButton')).toBe('Midira');
      expect(t('login.badgeId')).toBe('ID badge');
    });

    it('should translate dashboard', () => {
      expect(t('dashboard.scan')).toBe('Scan');
      expect(t('dashboard.history')).toBe('Tantara');
      expect(t('dashboard.profile')).toBe('Mombamomba');
    });

    it('should handle parameterized strings', () => {
      expect(t('history.totalScans', { count: 5 })).toBe('Scan 5 totaly');
    });
  });

  describe('Language switching', () => {
    it('should get current language', () => {
      expect(getLanguage()).toBe('fr');
      
      setLanguage('mg');
      expect(getLanguage()).toBe('mg');
      
      setLanguage('fr');
      expect(getLanguage()).toBe('fr');
    });

    it('should switch between languages', () => {
      expect(t('login.title')).toBe('Agent de collecte des taxes');
      
      setLanguage('mg');
      expect(t('login.title')).toBe('Mpangataka hetra');
      
      setLanguage('fr');
      expect(t('login.title')).toBe('Agent de collecte des taxes');
    });
  });

  describe('Missing keys', () => {
    it('should return key if translation not found', () => {
      expect(t('nonexistent.key')).toBe('nonexistent.key');
      expect(t('common.nonexistent')).toBe('common.nonexistent');
    });
  });
});