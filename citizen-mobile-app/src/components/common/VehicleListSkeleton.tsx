import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../../theme/colors';

interface VehicleListSkeletonProps {
  count?: number;
}

const VehicleListSkeleton: React.FC<VehicleListSkeletonProps> = ({ count = 3 }) => {
  return (
    <View style={styles.container}>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={styles.skeletonItem}>
          <View style={styles.skeletonHeader}>
            <View style={styles.skeletonTitle} />
            <View style={styles.skeletonBadge} />
          </View>
          <View style={styles.skeletonLine} />
          <View style={styles.skeletonLineShort} />
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
  skeletonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  skeletonTitle: {
    width: 120,
    height: 20,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
  },
  skeletonBadge: {
    width: 60,
    height: 20,
    backgroundColor: colors.skeleton,
    borderRadius: 10,
  },
  skeletonLine: {
    width: '100%',
    height: 16,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
    marginBottom: 8,
  },
  skeletonLineShort: {
    width: '60%',
    height: 16,
    backgroundColor: colors.skeleton,
    borderRadius: 4,
  },
});

export default VehicleListSkeleton;