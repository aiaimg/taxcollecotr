import React, { useCallback, useMemo } from 'react';
import { FlatList, FlatListProps, Dimensions } from 'react-native';

interface OptimizedFlatListProps<T> extends Omit<FlatListProps<T>, 'windowSize' | 'getItemLayout'> {
  itemHeight: number;
  windowSize?: number;
}

/**
 * Optimized FlatList component with performance improvements
 * Provides default optimizations for windowSize and getItemLayout
 */
export function OptimizedFlatList<T>({
  itemHeight,
  windowSize = 10,
  maxToRenderPerBatch = 10,
  initialNumToRender = 10,
  removeClippedSubviews = true,
  ...props
}: OptimizedFlatListProps<T>) {
  // Memoized getItemLayout for better performance
  const getItemLayout = useCallback(
    (data: ArrayLike<T> | null | undefined, index: number) => ({
      length: itemHeight,
      offset: itemHeight * index,
      index,
    }),
    [itemHeight]
  );

  // Memoized key extractor if not provided
  const keyExtractor = useMemo(() => {
    if (props.keyExtractor) {
      return props.keyExtractor;
    }
    return (item: any, index: number) => `item-${index}`;
  }, [props.keyExtractor]);

  return (
    <FlatList
      {...props}
      windowSize={windowSize}
      getItemLayout={getItemLayout}
      maxToRenderPerBatch={maxToRenderPerBatch}
      initialNumToRender={initialNumToRender}
      removeClippedSubviews={removeClippedSubviews}
      keyExtractor={keyExtractor}
    />
  );
}