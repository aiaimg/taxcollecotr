import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../../types/navigation';
import { UserType } from '../../types/models';
import { authService } from '../../services';
import {
  validateEmail,
  validatePhone,
  validatePassword,
  validatePasswordMatch,
  getPasswordStrength,
} from '../../utils/validation';
import { formatAPIError } from '../../api/interceptors';
import { colors } from '../../theme/colors';

type Props = NativeStackScreenProps<AuthStackParamList, 'Register'>;

interface FormData {
  user_type: UserType;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
  password_confirm: string;
  preferred_language: 'fr' | 'mg';
}

interface FormErrors {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  password?: string;
  password_confirm?: string;
}

export const RegisterScreen: React.FC<Props> = ({ navigation }) => {
  const { t, i18n } = useTranslation();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    user_type: 'PARTICULIER',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    password_confirm: '',
    preferred_language: i18n.language as 'fr' | 'mg',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const updateFormData = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field as keyof FormErrors]) {
      setErrors({ ...errors, [field]: undefined });
    }
  };

  const validateStep1 = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = t('auth.errors.firstNameRequired');
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = t('auth.errors.lastNameRequired');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = t('auth.errors.emailRequired');
    } else if (!validateEmail(formData.email)) {
      newErrors.email = t('auth.errors.emailInvalid');
    }

    if (!formData.phone) {
      newErrors.phone = t('auth.errors.phoneRequired');
    } else if (!validatePhone(formData.phone)) {
      newErrors.phone = t('auth.errors.phoneInvalid');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.password) {
      newErrors.password = t('auth.errors.passwordRequired');
    } else if (!validatePassword(formData.password)) {
      newErrors.password = t('auth.errors.passwordWeak');
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = t('auth.errors.passwordConfirmRequired');
    } else if (!validatePasswordMatch(formData.password, formData.password_confirm)) {
      newErrors.password_confirm = t('auth.errors.passwordMismatch');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    let isValid = false;

    if (step === 1) {
      isValid = validateStep1();
    } else if (step === 2) {
      isValid = validateStep2();
    }

    if (isValid && step < 3) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
      setErrors({});
    }
  };

  const handleRegister = async () => {
    if (!validateStep3()) {
      return;
    }

    setIsLoading(true);
    try {
      await authService.register(formData);
      Alert.alert(
        t('auth.register.success'),
        t('auth.register.verifyEmail'),
        [
          {
            text: t('common.ok'),
            onPress: () => navigation.navigate('Login'),
          },
        ]
      );
    } catch (error) {
      const errorMessage = formatAPIError(error);
      Alert.alert(t('auth.errors.registerFailed'), errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>{t('auth.register.step1Title')}</Text>

      <View style={styles.userTypeContainer}>
        <TouchableOpacity
          style={[
            styles.userTypeButton,
            formData.user_type === 'PARTICULIER' && styles.userTypeButtonActive,
          ]}
          onPress={() => updateFormData('user_type', 'PARTICULIER')}
        >
          <Text
            style={[
              styles.userTypeText,
              formData.user_type === 'PARTICULIER' && styles.userTypeTextActive,
            ]}
          >
            {t('auth.register.userTypeIndividual')}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.userTypeButton,
            formData.user_type === 'ENTREPRISE' && styles.userTypeButtonActive,
          ]}
          onPress={() => updateFormData('user_type', 'ENTREPRISE')}
        >
          <Text
            style={[
              styles.userTypeText,
              formData.user_type === 'ENTREPRISE' && styles.userTypeTextActive,
            ]}
          >
            {t('auth.register.userTypeBusiness')}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>{t('auth.firstName')}</Text>
        <TextInput
          style={[styles.input, errors.first_name && styles.inputError]}
          value={formData.first_name}
          onChangeText={(text) => updateFormData('first_name', text)}
          placeholder={t('auth.firstNamePlaceholder')}
          autoCapitalize="words"
          editable={!isLoading}
        />
        {errors.first_name && <Text style={styles.errorText}>{errors.first_name}</Text>}
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>{t('auth.lastName')}</Text>
        <TextInput
          style={[styles.input, errors.last_name && styles.inputError]}
          value={formData.last_name}
          onChangeText={(text) => updateFormData('last_name', text)}
          placeholder={t('auth.lastNamePlaceholder')}
          autoCapitalize="words"
          editable={!isLoading}
        />
        {errors.last_name && <Text style={styles.errorText}>{errors.last_name}</Text>}
      </View>
    </View>
  );

  const renderStep2 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>{t('auth.register.step2Title')}</Text>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>{t('auth.email')}</Text>
        <TextInput
          style={[styles.input, errors.email && styles.inputError]}
          value={formData.email}
          onChangeText={(text) => updateFormData('email', text)}
          placeholder={t('auth.emailPlaceholder')}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          editable={!isLoading}
        />
        {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>{t('auth.phone')}</Text>
        <TextInput
          style={[styles.input, errors.phone && styles.inputError]}
          value={formData.phone}
          onChangeText={(text) => updateFormData('phone', text)}
          placeholder="+261340000000"
          keyboardType="phone-pad"
          editable={!isLoading}
        />
        {errors.phone && <Text style={styles.errorText}>{errors.phone}</Text>}
        <Text style={styles.helperText}>{t('auth.phoneHelper')}</Text>
      </View>
    </View>
  );

  const renderStep3 = () => {
    const passwordStrength = formData.password ? getPasswordStrength(formData.password) : null;

    return (
      <View style={styles.stepContainer}>
        <Text style={styles.stepTitle}>{t('auth.register.step3Title')}</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>{t('auth.password')}</Text>
          <TextInput
            style={[styles.input, errors.password && styles.inputError]}
            value={formData.password}
            onChangeText={(text) => updateFormData('password', text)}
            placeholder={t('auth.passwordPlaceholder')}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isLoading}
          />
          {errors.password && <Text style={styles.errorText}>{errors.password}</Text>}
          {passwordStrength && (
            <View style={styles.passwordStrengthContainer}>
              <View
                style={[
                  styles.passwordStrengthBar,
                  passwordStrength === 'weak' && styles.passwordStrengthWeak,
                  passwordStrength === 'medium' && styles.passwordStrengthMedium,
                  passwordStrength === 'strong' && styles.passwordStrengthStrong,
                ]}
              />
              <Text style={styles.passwordStrengthText}>
                {t(`auth.passwordStrength.${passwordStrength}`)}
              </Text>
            </View>
          )}
          <Text style={styles.helperText}>{t('auth.passwordHelper')}</Text>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>{t('auth.passwordConfirm')}</Text>
          <TextInput
            style={[styles.input, errors.password_confirm && styles.inputError]}
            value={formData.password_confirm}
            onChangeText={(text) => updateFormData('password_confirm', text)}
            placeholder={t('auth.passwordConfirmPlaceholder')}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isLoading}
          />
          {errors.password_confirm && (
            <Text style={styles.errorText}>{errors.password_confirm}</Text>
          )}
        </View>

        <View style={styles.languageContainer}>
          <Text style={styles.label}>{t('auth.preferredLanguage')}</Text>
          <View style={styles.languageButtons}>
            <TouchableOpacity
              style={[
                styles.languageButton,
                formData.preferred_language === 'fr' && styles.languageButtonActive,
              ]}
              onPress={() => updateFormData('preferred_language', 'fr')}
            >
              <Text
                style={[
                  styles.languageText,
                  formData.preferred_language === 'fr' && styles.languageTextActive,
                ]}
              >
                Français
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.languageButton,
                formData.preferred_language === 'mg' && styles.languageButtonActive,
              ]}
              onPress={() => updateFormData('preferred_language', 'mg')}
            >
              <Text
                style={[
                  styles.languageText,
                  formData.preferred_language === 'mg' && styles.languageTextActive,
                ]}
              >
                Malagasy
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Text style={styles.title}>{t('auth.register.title')}</Text>
          <Text style={styles.subtitle}>
            {t('auth.register.step')} {step}/3
          </Text>
        </View>

        <View style={styles.progressBar}>
          <View style={[styles.progressSegment, step >= 1 && styles.progressSegmentActive]} />
          <View style={[styles.progressSegment, step >= 2 && styles.progressSegmentActive]} />
          <View style={[styles.progressSegment, step >= 3 && styles.progressSegmentActive]} />
        </View>

        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}

        <View style={styles.buttonContainer}>
          {step > 1 && (
            <TouchableOpacity
              style={styles.backButton}
              onPress={handleBack}
              disabled={isLoading}
            >
              <Text style={styles.backButtonText}>{t('common.back')}</Text>
            </TouchableOpacity>
          )}

          {step < 3 ? (
            <TouchableOpacity
              style={[styles.nextButton, step === 1 && styles.nextButtonFull]}
              onPress={handleNext}
              disabled={isLoading}
            >
              <Text style={styles.nextButtonText}>{t('common.next')}</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.registerButton, isLoading && styles.registerButtonDisabled]}
              onPress={handleRegister}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={colors.white} />
              ) : (
                <Text style={styles.registerButtonText}>{t('auth.register.button')}</Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.loginContainer}>
          <Text style={styles.loginText}>{t('auth.register.hasAccount')}</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')} disabled={isLoading}>
            <Text style={styles.loginLink}>{t('auth.login.button')}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.white,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  progressBar: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 32,
  },
  progressSegment: {
    flex: 1,
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
  },
  progressSegmentActive: {
    backgroundColor: colors.primary,
  },
  stepContainer: {
    marginBottom: 24,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 24,
  },
  userTypeContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  userTypeButton: {
    flex: 1,
    height: 50,
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  userTypeButtonActive: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryLight,
  },
  userTypeText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  userTypeTextActive: {
    color: colors.primary,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
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
  helperText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  passwordStrengthContainer: {
    marginTop: 8,
  },
  passwordStrengthBar: {
    height: 4,
    borderRadius: 2,
    marginBottom: 4,
  },
  passwordStrengthWeak: {
    width: '33%',
    backgroundColor: colors.error,
  },
  passwordStrengthMedium: {
    width: '66%',
    backgroundColor: colors.warning,
  },
  passwordStrengthStrong: {
    width: '100%',
    backgroundColor: colors.success,
  },
  passwordStrengthText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  languageContainer: {
    marginTop: 8,
  },
  languageButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  languageButton: {
    flex: 1,
    height: 44,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  languageButtonActive: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryLight,
  },
  languageText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  languageTextActive: {
    color: colors.primary,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  backButton: {
    flex: 1,
    height: 50,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
  },
  nextButton: {
    flex: 1,
    height: 50,
    backgroundColor: colors.primary,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  nextButtonFull: {
    flex: 1,
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  registerButton: {
    flex: 1,
    height: 50,
    backgroundColor: colors.primary,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  registerButtonDisabled: {
    opacity: 0.6,
  },
  registerButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  loginText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginRight: 4,
  },
  loginLink: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '600',
  },
});
