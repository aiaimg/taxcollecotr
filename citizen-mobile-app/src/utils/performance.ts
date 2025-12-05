import { useEffect, useRef } from 'react';

interface PerformanceMetrics {
  startTime: number;
  endTime?: number;
  duration?: number;
}

/**
 * Performance monitoring utilities for the app
 */
class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetrics> = new Map();
  private enabled = __DEV__; // Only enable in development mode

  /**
   * Start timing a specific operation
   */
  startTimer(name: string): void {
    if (!this.enabled) return;
    
    this.metrics.set(name, {
      startTime: Date.now(),
    });
  }

  /**
   * End timing and log the duration
   */
  endTimer(name: string): number | undefined {
    if (!this.enabled) return;

    const metric = this.metrics.get(name);
    if (!metric) {
      console.warn(`Timer '${name}' was not started`);
      return;
    }

    const endTime = Date.now();
    const duration = endTime - metric.startTime;

    this.metrics.set(name, {
      ...metric,
      endTime,
      duration,
    });

    console.log(`[Performance] ${name}: ${duration}ms`);
    return duration;
  }

  /**
   * Get all metrics
   */
  getMetrics(): Record<string, PerformanceMetrics> {
    const result: Record<string, PerformanceMetrics> = {};
    this.metrics.forEach((metric, name) => {
      result[name] = metric;
    });
    return result;
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics.clear();
  }
}

export const performanceMonitor = new PerformanceMonitor();

/**
 * Hook to measure component render time
 */
export function useRenderTime(componentName: string) {
  const renderStartTime = useRef<number>(Date.now());
  const renderCount = useRef<number>(0);

  useEffect(() => {
    renderCount.current += 1;
    const renderTime = Date.now() - renderStartTime.current;
    
    if (__DEV__) {
      console.log(`[Performance] ${componentName} render #${renderCount.current}: ${renderTime}ms`);
    }

    // Reset timer for next render
    renderStartTime.current = Date.now();
  });
}

/**
 * Hook to measure screen transition time
 */
export function useScreenTransition(screenName: string) {
  const transitionStartTime = useRef<number>(Date.now());

  useEffect(() => {
    const transitionTime = Date.now() - transitionStartTime.current;
    
    if (__DEV__) {
      console.log(`[Performance] ${screenName} transition: ${transitionTime}ms`);
    }

    return () => {
      // Measure time spent on screen
      const timeOnScreen = Date.now() - transitionStartTime.current;
      if (__DEV__) {
        console.log(`[Performance] ${screenName} time on screen: ${timeOnScreen}ms`);
      }
    };
  }, [screenName]);
}

/**
 * Measure app startup time
 */
export function measureAppStartup() {
  if (__DEV__) {
    const startupTime = Date.now() - (global as any).__APP_START_TIME__;
    console.log(`[Performance] App startup time: ${startupTime}ms`);
    return startupTime;
  }
  return 0;
}

// Set app start time when module loads
if (typeof global !== 'undefined') {
  (global as any).__APP_START_TIME__ = Date.now();
}