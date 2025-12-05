import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../../theme/colors';

interface PaymentListSkeletonProps {
  count?: number;
}

const PaymentListSkeleton: React.FC<PaymentListSkeletonProps> = ({ count = 3 }) => {
  return (
    <View style={styles.container}>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={styles.skeletonItem}>
          <View style={styles.skeletonLeft}>
            <View style={styles.skeletonTitle} />
            <View style={styles.skeletonSubtitle} />
          </View>
          <View style={styles.skeletonRight}>
            <View style={styles.skeletonAmount} />
            <View style={styles.skeletonStatus} />
          </View>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  skeletonItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  skeletonLeft: {
    flex: 1,
    marginRight: 16,
  },
  skeletonRight: {
    alignItems: 'flex-end',
  },
  skeletonTitle: {
    width: 100,
    height: 18,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
    marginBottom: 8,
  },
  skeletonSubtitle: {
    width: 80,
    height: 14,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
  },
  skeletonAmount: {
    width: 60,
    height: 18,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
    marginBottom: 8,
  },
  skeletonStatus: {
    width: 40,
    height: 14,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
  },
});

export default PaymentListSkeleton;