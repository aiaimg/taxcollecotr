import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Alert, Share } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import * as Brightness from 'expo-brightness';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';
import { typography } from '../../theme/typography';
import { OptimizedImage } from '../../components/common/OptimizedImage';
import { PaymentStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<PaymentStackParamList, 'QRCodeViewer'>;

export const QRCodeViewerScreen: React.FC<Props> = ({ navigation, route }) => {
  const { imageUrl, vehiclePlaque, paidAt, expiresAt, amount } = route.params;
  const [originalBrightness, setOriginalBrightness] = useState<number | null>(null);

  useEffect(() => {
    const boostBrightness = async () => {
      try {
        const sysBrightness = await Brightness.getBrightnessAsync();
        setOriginalBrightness(sysBrightness);
        await Brightness.setBrightnessAsync(1);
      } catch (e) {
        // ignore brightness errors
      }
    };
    boostBrightness();
    return () => {
      if (originalBrightness !== null) {
        Brightness.setBrightnessAsync(originalBrightness).catch(() => {});
      }
    };
  }, [originalBrightness]);

  const handleClose = () => {
    navigation.goBack();
  };

  const handleShare = async () => {
    try {
      await Share.share({
        message: `QR – ${vehiclePlaque}\nMontant: ${amount ?? ''}\nPayé le: ${paidAt ?? ''}\nLien: ${imageUrl}`,
      });
    } catch (e) {
      Alert.alert('Erreur', "Impossible de partager le code QR");
    }
  };

  const handleSave = async () => {
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', "Autorisez l'accès à la galerie pour enregistrer le QR");
        return;
      }
      const fileUri = `${FileSystem.cacheDirectory}qr_${Date.now()}.png`;
      const download = await FileSystem.downloadAsync(imageUrl, fileUri);
      await MediaLibrary.saveAsync(download.uri);
      Alert.alert('Succès', 'Code QR enregistré dans la galerie');
    } catch (e) {
      Alert.alert('Erreur', "Impossible d'enregistrer le code QR");
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleClose} style={styles.closeButton}>
          <Text style={styles.closeText}>✕</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Code QR</Text>
      </View>

      <View style={styles.qrContainer}>
        <OptimizedImage source={{ uri: imageUrl }} style={styles.qrImage} contentFit="contain" />
      </View>

      <View style={styles.infoContainer}>
        {vehiclePlaque && (
          <Text style={styles.infoText}>Véhicule: {vehiclePlaque}</Text>
        )}
        {amount !== undefined && (
          <Text style={styles.infoText}>Montant payé: {amount}</Text>
        )}
        {paidAt && (
          <Text style={styles.infoText}>Généré le: {new Date(paidAt).toLocaleString('fr-FR')}</Text>
        )}
        {expiresAt && (
          <Text style={styles.infoText}>Expire le: {new Date(expiresAt).toLocaleString('fr-FR')}</Text>
        )}
      </View>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
          <Text style={[styles.actionIcon, { color: colors.primary }]}>↗</Text>
          <Text style={styles.actionText}>Partager</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} onPress={handleSave}>
          <Text style={[styles.actionIcon, { color: colors.primary }]}>↓</Text>
          <Text style={styles.actionText}>Enregistrer</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.black,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  closeButton: {
    padding: spacing.sm,
    marginRight: spacing.sm,
  },
  closeText: {
    ...typography.h3,
    color: colors.white,
  },
  title: {
    ...typography.h3,
    color: colors.white,
  },
  qrContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  qrImage: {
    width: '100%',
    height: '100%',
  },
  infoContainer: {
    backgroundColor: colors.white,
    padding: spacing.md,
  },
  infoText: {
    ...typography.body,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    padding: spacing.md,
    backgroundColor: colors.white,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 8,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  actionIcon: {
    fontSize: 20,
    fontWeight: '600',
    marginRight: spacing.xs,
  },
  actionText: {
    ...typography.button,
    color: colors.primary,
  },
});

export default QRCodeViewerScreen;