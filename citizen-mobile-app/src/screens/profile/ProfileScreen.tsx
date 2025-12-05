import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import Ionicons from '@expo/vector-icons/Ionicons';

import { userProfileService } from '../../services/userProfileService';
import { UserProfile } from '../../types/models';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';

type RootStackParamList = {
  Profile: undefined;
  ProfileEdit: undefined;
  Settings: undefined;
};

type ProfileScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Profile'>;

const ProfileScreen: React.FC = () => {
  const { t } = useTranslation();
  const navigation = useNavigation<ProfileScreenNavigationProp>();
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const userProfile = await userProfileService.getProfile();
      setProfile(userProfile);
    } catch (error) {
      console.error('Error loading profile:', error);
      Alert.alert(
        t('profile.error.title'),
        t('profile.error.loadFailed'),
        [{ text: t('common.ok'), style: 'default' }]
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleEditProfile = () => {
    navigation.navigate('ProfileEdit');
  };

  const handleSettings = () => {
    navigation.navigate('Settings');
  };

  const handleRefresh = () => {
    loadProfile(true);
  };

  const getUserTypeLabel = (userType: string) => {
    switch (userType) {
      case 'PARTICULIER':
        return t('profile.userType.individual');
      case 'ENTREPRISE':
        return t('profile.userType.company');
      default:
        return userType;
    }
  };

  const getLanguageLabel = (language: string) => {
    switch (language) {
      case 'fr':
        return t('profile.language.french');
      case 'mg':
        return t('profile.language.malagasy');
      default:
        return language;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>{t('profile.loading')}</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="person-circle-outline" size={64} color={colors.text.secondary} />
        <Text style={styles.errorText}>{t('profile.error.notFound')}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={handleRefresh}>
          <Text style={styles.retryButtonText}>{t('common.retry')}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { user, profile_picture, preferred_language, notifications_enabled, biometric_enabled } = profile;
  const fullName = `${user.first_name} ${user.last_name}`;

  return (
    <ScrollView 
      style={styles.container}
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={handleRefresh}
          colors={[colors.primary]}
        />
      }
    >
      <View style={styles.header}>
        <View style={styles.profileImageContainer}>
          {profile_picture ? (
            <Image source={{ uri: profile_picture }} style={styles.profileImage} />
          ) : (
            <View style={styles.profileImagePlaceholder}>
              <Ionicons name="person" size={48} color={colors.white} />
            </View>
          )}
        </View>
        <Text style={styles.nameText}>{fullName}</Text>
        <Text style={styles.emailText}>{user.email}</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.personalInfo')}</Text>
          
          <View style={styles.infoRow}>
            <Ionicons name="person-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.name')}</Text>
              <Text style={styles.infoValue}>{fullName}</Text>
            </View>
          </View>

          <View style={styles.infoRow}>
            <Ionicons name="mail-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.email')}</Text>
              <Text style={styles.infoValue}>{user.email}</Text>
            </View>
          </View>

          <View style={styles.infoRow}>
            <Ionicons name="call-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.phone')}</Text>
              <Text style={styles.infoValue}>{user.phone}</Text>
            </View>
          </View>

          <View style={styles.infoRow}>
            <Ionicons name="business-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.userType')}</Text>
              <Text style={styles.infoValue}>{getUserTypeLabel(user.user_type)}</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('profile.preferences')}</Text>
          
          <View style={styles.infoRow}>
            <Ionicons name="language-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.language')}</Text>
              <Text style={styles.infoValue}>{getLanguageLabel(preferred_language)}</Text>
            </View>
          </View>

          <View style={styles.infoRow}>
            <Ionicons 
              name={notifications_enabled ? "notifications-outline" : "notifications-off-outline"} 
              size={20} 
              color={colors.text.secondary} 
            />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.notifications')}</Text>
              <Text style={styles.infoValue}>
                {notifications_enabled ? t('common.enabled') : t('common.disabled')}
              </Text>
            </View>
          </View>

          <View style={styles.infoRow}>
            <Ionicons name="finger-print-outline" size={20} color={colors.text.secondary} />
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>{t('profile.biometric')}</Text>
              <Text style={styles.infoValue}>
                {biometric_enabled ? t('common.enabled') : t('common.disabled')}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.editButton} onPress={handleEditProfile}>
            <Ionicons name="create-outline" size={20} color={colors.white} />
            <Text style={styles.editButtonText}>{t('profile.editProfile')}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingsButton} onPress={handleSettings}>
            <Ionicons name="settings-outline" size={20} color={colors.primary} />
            <Text style={styles.settingsButtonText}>{t('profile.settings')}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.xl,
  },
  errorText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: spacing.lg,
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 8,
  },
  retryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
  },
  header: {
    backgroundColor: colors.primary,
    paddingTop: spacing.xl + 20,
    paddingBottom: spacing.xl,
    alignItems: 'center',
  },
  profileImageContainer: {
    marginBottom: spacing.md,
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: colors.white,
  },
  profileImagePlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primaryDark,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: colors.white,
  },
  nameText: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.white,
    marginBottom: spacing.xs,
  },
  emailText: {
    fontSize: typography.fontSize.base,
    color: colors.white,
    opacity: 0.9,
  },
  content: {
    padding: spacing.lg,
  },
  section: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  infoTextContainer: {
    flex: 1,
    marginLeft: spacing.md,
  },
  infoLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    marginBottom: 2,
  },
  infoValue: {
    fontSize: typography.fontSize.base,
    color: colors.text.primary,
    fontWeight: typography.fontWeight.medium,
  },
  buttonContainer: {
    marginTop: spacing.lg,
  },
  editButton: {
    backgroundColor: colors.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: 8,
    marginBottom: spacing.md,
  },
  editButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    marginLeft: spacing.sm,
  },
  settingsButton: {
    backgroundColor: colors.white,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  settingsButtonText: {
    color: colors.primary,
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    marginLeft: spacing.sm,
  },
});

export default ProfileScreen;