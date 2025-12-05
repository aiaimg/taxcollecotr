import { useEffect } from 'react';
import { useNavigation } from '@react-navigation/native';
import { vehicleApi } from '../store/api/vehicleApi';
import { taxApi } from '../store/api/taxApi';
import { useAppDispatch } from '../store/hooks';

interface PrefetchOptions {
  vehiclePlaque?: string;
  paymentId?: number;
}

/**
 * Hook to prefetch data for likely next screens
 * Improves perceived performance by loading data before navigation
 */
export function usePrefetchData({ vehiclePlaque, paymentId }: PrefetchOptions = {}) {
  const dispatch = useAppDispatch();

  // Prefetch vehicle data if plaque is provided
  useEffect(() => {
    if (vehiclePlaque) {
      // Prefetch vehicle details
      dispatch(
        vehicleApi.util.prefetch('getVehicle', vehiclePlaque, {
          force: false, // Don't refetch if already cached
        })
      );

      // Prefetch vehicle tax info
      dispatch(
        vehicleApi.util.prefetch('getVehicleTaxInfo', vehiclePlaque, {
          force: false,
        })
      );
    }
  }, [dispatch, vehiclePlaque]);

  // Prefetch payment data if paymentId is provided
  useEffect(() => {
    if (paymentId) {
      // Prefetch payment status
      dispatch(
        taxApi.util.prefetch('getPaymentStatus', paymentId, {
          force: false,
        })
      );

      // Prefetch payment receipt
      dispatch(
        taxApi.util.prefetch('getPaymentReceipt', paymentId, {
          force: false,
        })
      );
    }
  }, [dispatch, paymentId]);
}

/**
 * Prefetch payment history when user is likely to view it
 * Call this when user navigates to dashboard or payment-related screens
 */
export function usePrefetchPaymentHistory() {
  const dispatch = useAppDispatch();

  return () => {
    dispatch(
      taxApi.util.prefetch('getPaymentHistory', { page: 1, pageSize: 20 }, {
        force: false,
      })
    );
  };
}

/**
 * Prefetch vehicle list when user is likely to view it
 * Call this when user navigates to dashboard or vehicle-related screens
 */
export function usePrefetchVehicleList() {
  const dispatch = useAppDispatch();

  return () => {
    dispatch(
      vehicleApi.util.prefetch('getVehicles', undefined, {
        force: false,
      })
    );
  };
}