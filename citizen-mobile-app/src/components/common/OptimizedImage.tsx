import React from 'react';
import { Image } from 'expo-image';
import { StyleSheet, View, ActivityIndicator } from 'react-native';
import { colors } from '../../theme/colors';

interface OptimizedImageProps {
  source: string | { uri: string };
  style?: any;
  placeholder?: string;
  contentFit?: 'cover' | 'contain' | 'fill' | 'none' | 'scale-down';
  cachePolicy?: 'none' | 'disk' | 'memory' | 'memory-disk';
  onLoad?: () => void;
  onError?: (error: any) => void;
}

/**
 * Optimized Image Component using expo-image
 * Provides better performance with caching, lazy loading, and memory management
 */
export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  source,
  style,
  placeholder = '🖼️',
  contentFit = 'cover',
  cachePolicy = 'memory-disk',
  onLoad,
  onError,
}) => {
  const imageSource = typeof source === 'string' ? source : source.uri;

  return (
    <View style={[styles.container, style]}>
      <Image
        source={imageSource}
        style={StyleSheet.absoluteFillObject}
        contentFit={contentFit}
        cachePolicy={cachePolicy}
        placeholder={placeholder}
        transition={200}
        onLoad={onLoad}
        onError={onError}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
});