import * as ImageManipulator from 'expo-image-manipulator';
import type {
  Vehicle,
  VehicleFormData,
  VehicleDocument,
  VehicleType,
} from '../types/models';

/**
 * Service for vehicle-related operations
 * Handles image compression, form data preparation, and utility functions
 */
class VehicleService {
  /**
   * Compress image before upload
   * @param uri - Image URI
   * @returns Compressed image URI
   */
  async compressImage(uri: string): Promise<string> {
    try {
      const manipResult = await ImageManipulator.manipulateAsync(
        uri,
        [{ resize: { width: 1024 } }], // Resize to max 1024px width
        { 
          compress: 0.8, // 80% quality
          format: ImageManipulator.SaveFormat.JPEG
        }
      );
      return manipResult.uri;
    } catch (error) {
      console.warn('Image compression failed, using original:', error);
      return uri;
    }
  }

  /**
   * Pick image from camera or gallery
   * @param source - 'camera' or 'gallery'
   * @returns Image URI or null
   */
  async pickImage(
    source: 'camera' | 'gallery'
  ): Promise<string | null> {
    // TODO: Implement image picker when expo-image-picker is installed
    return null;
  }

  /**
   * Generate temporary plaque for vehicles without plates
   * @returns Generated plaque string
   */
  generateTemporaryPlaque(): string {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `TEMP-${timestamp}-${random}`;
  }

  /**
   * Suggest puissance fiscale based on cylindrée
   * @param cylindree - Engine displacement in cm³
   * @returns Suggested puissance fiscale in CV
   */
  suggestPuissanceFiscale(cylindree: number): number {
    // Formula: CV = (cylindrée / 200) rounded up
    // This is a simplified formula, actual calculation may vary
    if (cylindree <= 0) return 0;
    return Math.ceil(cylindree / 200);
  }

  /**
   * Check if cylindrée and puissance fiscale are coherent
   * @param cylindree - Engine displacement in cm³
   * @param puissanceFiscale - Fiscal power in CV
   * @returns true if coherent, false otherwise
   */
  isCoherent(cylindree: number, puissanceFiscale: number): boolean {
    const suggested = this.suggestPuissanceFiscale(cylindree);
    // Allow ±2 CV tolerance
    return Math.abs(suggested - puissanceFiscale) <= 2;
  }

  /**
   * Prepare FormData for vehicle creation/update
   * @param data - Vehicle form data
   * @returns FormData ready for API submission
   */
  async prepareFormData(data: VehicleFormData): Promise<FormData> {
    const formData = new FormData();

    // Add basic fields
    if (data.plaque_immatriculation && !data.sans_plaque) {
      formData.append('plaque_immatriculation', data.plaque_immatriculation);
    }
    formData.append('sans_plaque', data.sans_plaque ? 'true' : 'false');
    formData.append('marque', data.marque);
    formData.append('modele', data.modele);
    formData.append('couleur', data.couleur);
    
    if (data.vin) {
      formData.append('vin', data.vin);
    }

    // Add technical specifications
    formData.append('type_vehicule_id', data.type_vehicule_id.toString());
    formData.append('puissance_fiscale_cv', data.puissance_fiscale_cv.toString());
    formData.append('cylindree_cm3', data.cylindree_cm3.toString());
    formData.append('source_energie', data.source_energie);
    formData.append('date_premiere_circulation', data.date_premiere_circulation);
    formData.append('categorie_vehicule', data.categorie_vehicule);

    // Add documents if present
    if (data.documents && data.documents.length > 0) {
      for (const doc of data.documents) {
        // Compress image before adding to form
        const compressedUri = await this.compressImage(doc.uri);
        
        // Create file object
        const file = {
          uri: compressedUri,
          type: 'image/jpeg',
          name: doc.name || `${doc.type}.jpg`,
        } as any;

        formData.append(doc.type, file);
      }
    }

    return formData;
  }

  /**
   * Validate vehicle form data
   * @param data - Vehicle form data
   * @returns Object with validation errors (empty if valid)
   */
  validateVehicleForm(data: Partial<VehicleFormData>): Record<string, string> {
    const errors: Record<string, string> = {};

    // Validate plaque if not sans_plaque
    if (!data.sans_plaque && !data.plaque_immatriculation?.trim()) {
      errors.plaque_immatriculation = 'Plaque d\'immatriculation requise';
    }

    // Validate basic info
    if (!data.marque?.trim()) {
      errors.marque = 'Marque requise';
    }
    if (!data.modele?.trim()) {
      errors.modele = 'Modèle requis';
    }
    if (!data.couleur?.trim()) {
      errors.couleur = 'Couleur requise';
    }

    // Validate technical specs
    if (!data.type_vehicule_id) {
      errors.type_vehicule_id = 'Type de véhicule requis';
    }
    if (!data.puissance_fiscale_cv || data.puissance_fiscale_cv <= 0) {
      errors.puissance_fiscale_cv = 'Puissance fiscale invalide';
    }
    if (!data.cylindree_cm3 || data.cylindree_cm3 <= 0) {
      errors.cylindree_cm3 = 'Cylindrée invalide';
    }
    if (!data.source_energie) {
      errors.source_energie = 'Source d\'énergie requise';
    }
    if (!data.date_premiere_circulation) {
      errors.date_premiere_circulation = 'Date de première circulation requise';
    }
    if (!data.categorie_vehicule) {
      errors.categorie_vehicule = 'Catégorie requise';
    }

    return errors;
  }

  /**
   * Format vehicle display name
   * @param vehicle - Vehicle object
   * @returns Formatted display name
   */
  getVehicleDisplayName(vehicle: Vehicle): string {
    return `${vehicle.marque} ${vehicle.modele}`;
  }

  /**
   * Get tax status color
   * @param status - Tax status
   * @returns Color code
   */
  getTaxStatusColor(status: Vehicle['tax_status']): string {
    switch (status) {
      case 'PAYE':
        return '#10b981'; // green
      case 'IMPAYE':
        return '#f59e0b'; // orange
      case 'EXPIRE':
        return '#ef4444'; // red
      case 'EXONERE':
        return '#3b82f6'; // blue
      default:
        return '#6b7280'; // gray
    }
  }

  /**
   * Get tax status label
   * @param status - Tax status
   * @returns Localized label
   */
  getTaxStatusLabel(status: Vehicle['tax_status']): string {
    switch (status) {
      case 'PAYE':
        return '✓ Payé';
      case 'IMPAYE':
        return '! À payer';
      case 'EXPIRE':
        return '✗ Expiré';
      case 'EXONERE':
        return 'ⓘ Exonéré';
      default:
        return 'Inconnu';
    }
  }
}

export default new VehicleService();
