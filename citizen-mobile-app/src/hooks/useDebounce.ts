import { useState, useEffect, useCallback } from 'react';
import debounce from 'lodash.debounce';

interface UseDebounceProps<T> {
  value: T;
  delay?: number;
}

/**
 * Custom hook for debouncing values
 * Useful for search inputs to reduce API calls
 */
export function useDebounce<T>({ value, delay = 500 }: UseDebounceProps<T>): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cleanup timeout on value change
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

interface UseDebouncedSearchProps {
  onSearch: (query: string) => void;
  delay?: number;
}

/**
 * Custom hook for debounced search
 * Provides a search function that automatically debounces calls
 */
export function useDebouncedSearch({ onSearch, delay = 500 }: UseDebouncedSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearchQuery = useDebounce({ value: searchQuery, delay });

  // Create debounced search function
  const debouncedSearch = useCallback(
    debounce((query: string) => {
      onSearch(query);
    }, delay),
    [onSearch, delay]
  );

  // Trigger search when debounced value changes
  useEffect(() => {
    if (debouncedSearchQuery.trim()) {
      debouncedSearch(debouncedSearchQuery);
    } else {
      // If query is empty, call search immediately with empty string
      onSearch('');
    }
  }, [debouncedSearchQuery, debouncedSearch, onSearch]);

  return {
    searchQuery,
    setSearchQuery,
    debouncedQuery: debouncedSearchQuery,
  };
}