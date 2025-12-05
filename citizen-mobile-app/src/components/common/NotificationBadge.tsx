import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAppSelector } from '../../store';
import { colors } from '../../theme/colors';
import { typography } from '../../theme/typography';

interface NotificationBadgeProps {
  size?: 'small' | 'medium';
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({ size = 'small' }) => {
  const unreadCount = useAppSelector(state => state.notifications.unreadCount);

  if (unreadCount === 0) {
    return null;
  }

  const sizeStyles = size === 'small' ? styles.badgeSmall : styles.badgeMedium;
  const textSize = size === 'small' ? styles.badgeTextSmall : styles.badgeTextMedium;

  return (
    <View style={[styles.badge, sizeStyles]}>
      <Text style={[styles.badgeText, textSize]}>
        {unreadCount > 99 ? '99+' : unreadCount}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    backgroundColor: colors.error,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: -5,
    right: -5,
    zIndex: 1,
  },
  badgeSmall: {
    minWidth: 16,
    height: 16,
    paddingHorizontal: 4,
  },
  badgeMedium: {
    minWidth: 20,
    height: 20,
    paddingHorizontal: 6,
  },
  badgeText: {
    color: colors.white,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  badgeTextSmall: {
    fontSize: 10,
  },
  badgeTextMedium: {
    fontSize: 12,
  },
});