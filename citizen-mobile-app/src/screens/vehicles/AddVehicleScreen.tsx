import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Switch,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import {
  useCreateVehicleMutation,
  useGetVehicleTypesQuery,
} from '../../store/api/vehicleApi';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import vehicleService from '../../services/vehicleService';
import { VehicleFormData, VehicleDocument } from '../../types/models';
import { colors } from '../../theme/colors';
import useNetworkStatus from '../../hooks/useNetworkStatus';
import OfflineIndicator from '../../components/common/OfflineIndicator';

type NavigationProp = NativeStackNavigationProp<any>;

/**
 * Add Vehicle Screen
 * Multi-step form for adding a new vehicle
 */
export const AddVehicleScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();
  const { t } = useTranslation();
  const user = useSelector((state: RootState) => state.auth.user);
  const { isOnline } = useNetworkStatus();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<VehicleFormData>>({
    sans_plaque: false,
    documents: [],
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: vehicleTypes } = useGetVehicleTypesQuery();
  const [createVehicle, { isLoading }] = useCreateVehicleMutation();

  const totalSteps = 4;

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.sans_plaque && !formData.plaque_immatriculation?.trim()) {
          newErrors.plaque_immatriculation = 'Plaque requise';
        }
        if (!formData.marque?.trim()) {
          newErrors.marque = 'Marque requise';
        }
        if (!formData.modele?.trim()) {
          newErrors.modele = 'Modèle requis';
        }
        if (!formData.couleur?.trim()) {
          newErrors.couleur = 'Couleur requise';
        }
        break;

      case 2:
        if (!formData.type_vehicule_id) {
          newErrors.type_vehicule_id = 'Type requis';
        }
        if (!formData.puissance_fiscale_cv || formData.puissance_fiscale_cv <= 0) {
          newErrors.puissance_fiscale_cv = 'Puissance invalide';
        }
        if (!formData.cylindree_cm3 || formData.cylindree_cm3 <= 0) {
          newErrors.cylindree_cm3 = 'Cylindrée invalide';
        }
        if (!formData.source_energie) {
          newErrors.source_energie = 'Source d\'énergie requise';
        }
        if (!formData.date_premiere_circulation) {
          newErrors.date_premiere_circulation = 'Date requise';
        }
        break;

      case 3:
        if (!formData.categorie_vehicule) {
          newErrors.categorie_vehicule = 'Catégorie requise';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) {
      return;
    }

    if (!isOnline) {
      Alert.alert(
        t('common.offline', 'Mode hors ligne'),
        t('vehicles.offlineVehicleMessage', 'L\'ajout de véhicule nécessite une connexion internet. Veuillez vous connecter pour continuer.'),
        [{ text: t('common.ok', 'OK') }]
      );
      return;
    }

    try {
      // Generate temporary plaque if sans_plaque
      const dataToSubmit = { ...formData } as VehicleFormData;
      if (formData.sans_plaque && !formData.plaque_immatriculation) {
        dataToSubmit.plaque_immatriculation = vehicleService.generateTemporaryPlaque();
      }

      // Prepare form data
      const preparedData = await vehicleService.prepareFormData(dataToSubmit);
      
      // Submit
      await createVehicle(preparedData).unwrap();
      
      Alert.alert(
        'Succès',
        'Véhicule ajouté avec succès',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      Alert.alert(
        'Erreur',
        error?.data?.message || 'Impossible d\'ajouter le véhicule'
      );
    }
  };

  const handlePickImage = async (documentType: VehicleDocument['type']) => {
    try {
      const uri = await vehicleService.pickImage('gallery');
      if (uri) {
        const newDoc: VehicleDocument = {
          type: documentType,
          uri,
          name: `${documentType}.jpg`,
        };
        
        const existingDocs = formData.documents || [];
        const filteredDocs = existingDocs.filter(d => d.type !== documentType);
        
        updateFormData('documents', [...filteredDocs, newDoc]);
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
    }
  };

  const renderStepIndicator = () => (
    <View style={styles.stepIndicator}>
      {Array.from({ length: totalSteps }).map((_, index) => (
        <View
          key={index}
          style={[
            styles.stepDot,
            index + 1 === currentStep && styles.stepDotActive,
            index + 1 < currentStep && styles.stepDotCompleted,
          ]}
        />
      ))}
    </View>
  );

  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Informations de base</Text>

      <View style={styles.switchRow}>
        <Text style={styles.label}>Véhicule sans plaque</Text>
        <Switch
          value={formData.sans_plaque}
          onValueChange={(value) => updateFormData('sans_plaque', value)}
          trackColor={{ false: colors.gray300, true: colors.primary }}
          thumbColor={colors.white}
        />
      </View>

      {!formData.sans_plaque && (
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Plaque d'immatriculation *</Text>
          <TextInput
            style={[styles.input, errors.plaque_immatriculation && styles.inputError]}
            value={formData.plaque_immatriculation}
            onChangeText={(value) => updateFormData('plaque_immatriculation', value.toUpperCase())}
            placeholder="Ex: 1234 TBA"
            autoCapitalize="characters"
          />
          {errors.plaque_immatriculation && (
            <Text style={styles.errorText}>{errors.plaque_immatriculation}</Text>
          )}
        </View>
      )}

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Marque *</Text>
        <TextInput
          style={[styles.input, errors.marque && styles.inputError]}
          value={formData.marque}
          onChangeText={(value) => updateFormData('marque', value)}
          placeholder="Ex: Toyota"
        />
        {errors.marque && <Text style={styles.errorText}>{errors.marque}</Text>}
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Modèle *</Text>
        <TextInput
          style={[styles.input, errors.modele && styles.inputError]}
          value={formData.modele}
          onChangeText={(value) => updateFormData('modele', value)}
          placeholder="Ex: Corolla"
        />
        {errors.modele && <Text style={styles.errorText}>{errors.modele}</Text>}
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Couleur *</Text>
        <TextInput
          style={[styles.input, errors.couleur && styles.inputError]}
          value={formData.couleur}
          onChangeText={(value) => updateFormData('couleur', value)}
          placeholder="Ex: Blanc"
        />
        {errors.couleur && <Text style={styles.errorText}>{errors.couleur}</Text>}
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>VIN (optionnel)</Text>
        <TextInput
          style={styles.input}
          value={formData.vin}
          onChangeText={(value) => updateFormData('vin', value.toUpperCase())}
          placeholder="Ex: 1HGBH41JXMN109186"
          autoCapitalize="characters"
        />
      </View>
    </View>
  );

  const renderStep2 = () => {
    // Check coherence when cylindree or puissance changes
    const checkCoherence = () => {
      if (formData.cylindree_cm3 && formData.puissance_fiscale_cv) {
        return vehicleService.isCoherent(
          formData.cylindree_cm3,
          formData.puissance_fiscale_cv
        );
      }
      return true;
    };

    const suggestPuissance = () => {
      if (formData.cylindree_cm3) {
        const suggested = vehicleService.suggestPuissanceFiscale(formData.cylindree_cm3);
        updateFormData('puissance_fiscale_cv', suggested);
      }
    };

    return (
      <View style={styles.stepContainer}>
        <Text style={styles.stepTitle}>Spécifications techniques</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Type de véhicule *</Text>
          <View style={styles.pickerContainer}>
            {vehicleTypes?.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.pickerOption,
                  formData.type_vehicule_id === type.id && styles.pickerOptionSelected,
                ]}
                onPress={() => updateFormData('type_vehicule_id', type.id)}
              >
                <Text
                  style={[
                    styles.pickerOptionText,
                    formData.type_vehicule_id === type.id && styles.pickerOptionTextSelected,
                  ]}
                >
                  {type.nom}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          {errors.type_vehicule_id && (
            <Text style={styles.errorText}>{errors.type_vehicule_id}</Text>
          )}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Cylindrée (cm³) *</Text>
          <TextInput
            style={[styles.input, errors.cylindree_cm3 && styles.inputError]}
            value={formData.cylindree_cm3?.toString()}
            onChangeText={(value) => {
              const num = parseInt(value) || 0;
              updateFormData('cylindree_cm3', num);
            }}
            onBlur={suggestPuissance}
            placeholder="Ex: 1500"
            keyboardType="numeric"
          />
          {errors.cylindree_cm3 && (
            <Text style={styles.errorText}>{errors.cylindree_cm3}</Text>
          )}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Puissance fiscale (CV) *</Text>
          <TextInput
            style={[styles.input, errors.puissance_fiscale_cv && styles.inputError]}
            value={formData.puissance_fiscale_cv?.toString()}
            onChangeText={(value) => {
              const num = parseInt(value) || 0;
              updateFormData('puissance_fiscale_cv', num);
            }}
            placeholder="Ex: 8"
            keyboardType="numeric"
          />
          {errors.puissance_fiscale_cv && (
            <Text style={styles.errorText}>{errors.puissance_fiscale_cv}</Text>
          )}
          {!checkCoherence() && (
            <Text style={styles.warningText}>
              ⚠️ La puissance fiscale semble incohérente avec la cylindrée
            </Text>
          )}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Source d'énergie *</Text>
          <View style={styles.pickerContainer}>
            {['ESSENCE', 'DIESEL', 'ELECTRIQUE', 'HYBRIDE'].map((source) => (
              <TouchableOpacity
                key={source}
                style={[
                  styles.pickerOption,
                  formData.source_energie === source && styles.pickerOptionSelected,
                ]}
                onPress={() => updateFormData('source_energie', source)}
              >
                <Text
                  style={[
                    styles.pickerOptionText,
                    formData.source_energie === source && styles.pickerOptionTextSelected,
                  ]}
                >
                  {source}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          {errors.source_energie && (
            <Text style={styles.errorText}>{errors.source_energie}</Text>
          )}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Date de première circulation *</Text>
          <TextInput
            style={[styles.input, errors.date_premiere_circulation && styles.inputError]}
            value={formData.date_premiere_circulation}
            onChangeText={(value) => updateFormData('date_premiere_circulation', value)}
            placeholder="YYYY-MM-DD"
          />
          {errors.date_premiere_circulation && (
            <Text style={styles.errorText}>{errors.date_premiere_circulation}</Text>
          )}
        </View>
      </View>
    );
  };

  const renderStep3 = () => {
    const categories = user?.user_type === 'ENTREPRISE'
      ? ['PERSONNEL', 'COMMERCIAL']
      : ['PERSONNEL'];

    return (
      <View style={styles.stepContainer}>
        <Text style={styles.stepTitle}>Catégorie du véhicule</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Catégorie *</Text>
          <View style={styles.pickerContainer}>
            {categories.map((cat) => (
              <TouchableOpacity
                key={cat}
                style={[
                  styles.pickerOption,
                  formData.categorie_vehicule === cat && styles.pickerOptionSelected,
                ]}
                onPress={() => updateFormData('categorie_vehicule', cat)}
              >
                <Text
                  style={[
                    styles.pickerOptionText,
                    formData.categorie_vehicule === cat && styles.pickerOptionTextSelected,
                  ]}
                >
                  {cat}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          {errors.categorie_vehicule && (
            <Text style={styles.errorText}>{errors.categorie_vehicule}</Text>
          )}
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            {user?.user_type === 'ENTREPRISE'
              ? 'Les entreprises peuvent enregistrer des véhicules personnels ou commerciaux.'
              : 'Les particuliers ne peuvent enregistrer que des véhicules personnels.'}
          </Text>
        </View>
      </View>
    );
  };

  const renderStep4 = () => {
    const hasDocument = (type: VehicleDocument['type']) =>
      formData.documents?.some(d => d.type === type);

    return (
      <View style={styles.stepContainer}>
        <Text style={styles.stepTitle}>Documents (optionnel)</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Carte grise (recto)</Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => handlePickImage('carte_grise')}
          >
            <Text style={styles.uploadButtonText}>
              {hasDocument('carte_grise') ? '✓ Image sélectionnée' : 'Sélectionner une image'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Carte grise (verso)</Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => handlePickImage('carte_grise_verso')}
          >
            <Text style={styles.uploadButtonText}>
              {hasDocument('carte_grise_verso') ? '✓ Image sélectionnée' : 'Sélectionner une image'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Assurance</Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => handlePickImage('assurance')}
          >
            <Text style={styles.uploadButtonText}>
              {hasDocument('assurance') ? '✓ Image sélectionnée' : 'Sélectionner une image'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Contrôle technique</Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => handlePickImage('controle_technique')}
          >
            <Text style={styles.uploadButtonText}>
              {hasDocument('controle_technique') ? '✓ Image sélectionnée' : 'Sélectionner une image'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            Les documents sont optionnels mais recommandés pour faciliter la vérification.
          </Text>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Offline Indicator */}
      <OfflineIndicator compact={true} showSyncInfo={true} />
      
      {renderStepIndicator()}

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
      </ScrollView>

      <View style={styles.footer}>
        <View style={styles.buttonRow}>
          {currentStep > 1 && (
            <TouchableOpacity
              style={[styles.button, styles.buttonSecondary]}
              onPress={handlePrevious}
            >
              <Text style={styles.buttonSecondaryText}>Précédent</Text>
            </TouchableOpacity>
          )}

          {currentStep < totalSteps ? (
            <TouchableOpacity
              style={[styles.button, styles.buttonPrimary, currentStep === 1 && styles.buttonFull]}
              onPress={handleNext}
            >
              <Text style={styles.buttonPrimaryText}>Suivant</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.button, styles.buttonPrimary]}
              onPress={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator size="small" color={colors.white} />
              ) : (
                <Text style={styles.buttonPrimaryText}>Ajouter le véhicule</Text>
              )}
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundSecondary,
  },
  stepIndicator: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  stepDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.gray300,
    marginHorizontal: 6,
  },
  stepDotActive: {
    backgroundColor: colors.primary,
    width: 16,
    height: 16,
    borderRadius: 8,
  },
  stepDotCompleted: {
    backgroundColor: colors.success,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  stepContainer: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 20,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    color: colors.textPrimary,
    backgroundColor: colors.white,
  },
  inputError: {
    borderColor: colors.error,
  },
  errorText: {
    fontSize: 12,
    color: colors.error,
    marginTop: 4,
  },
  warningText: {
    fontSize: 12,
    color: colors.warning,
    marginTop: 4,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    paddingVertical: 8,
  },
  pickerContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  pickerOption: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.white,
  },
  pickerOptionSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  pickerOptionText: {
    fontSize: 14,
    color: colors.textPrimary,
  },
  pickerOptionTextSelected: {
    color: colors.white,
    fontWeight: '600',
  },
  uploadButton: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    borderStyle: 'dashed',
    paddingVertical: 20,
    alignItems: 'center',
    backgroundColor: colors.backgroundSecondary,
  },
  uploadButtonText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  infoBox: {
    backgroundColor: colors.backgroundSecondary,
    borderRadius: 8,
    padding: 12,
    marginTop: 16,
  },
  infoText: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  footer: {
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    padding: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonFull: {
    flex: 1,
  },
  buttonPrimary: {
    backgroundColor: colors.primary,
  },
  buttonPrimaryText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  buttonSecondary: {
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonSecondaryText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
  },
});
