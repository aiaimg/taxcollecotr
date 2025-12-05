import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Vehicle, VehicleType } from '../../types/models';

/**
 * Vehicle State Interface
 * Manages vehicle-related state including list, selected vehicle, and types
 */
interface VehicleState {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  vehicleTypes: VehicleType[];
  isLoading: boolean;
  error: string | null;
}

/**
 * Initial State
 */
const initialState: VehicleState = {
  vehicles: [],
  selectedVehicle: null,
  vehicleTypes: [],
  isLoading: false,
  error: null,
};

/**
 * Vehicle Slice
 * Manages local vehicle state (complementary to RTK Query cache)
 */
const vehicleSlice = createSlice({
  name: 'vehicles',
  initialState,
  reducers: {
    // Set vehicles list
    setVehicles: (state, action: PayloadAction<Vehicle[]>) => {
      state.vehicles = action.payload;
      state.error = null;
    },

    // Add a vehicle to the list
    addVehicle: (state, action: PayloadAction<Vehicle>) => {
      state.vehicles.push(action.payload);
      state.error = null;
    },

    // Update a vehicle in the list
    updateVehicle: (state, action: PayloadAction<Vehicle>) => {
      const index = state.vehicles.findIndex(
        v => v.plaque_immatriculation === action.payload.plaque_immatriculation
      );
      if (index !== -1) {
        state.vehicles[index] = action.payload;
      }
      // Update selected vehicle if it's the same one
      if (
        state.selectedVehicle?.plaque_immatriculation ===
        action.payload.plaque_immatriculation
      ) {
        state.selectedVehicle = action.payload;
      }
      state.error = null;
    },

    // Remove a vehicle from the list
    removeVehicle: (state, action: PayloadAction<string>) => {
      state.vehicles = state.vehicles.filter(
        v => v.plaque_immatriculation !== action.payload
      );
      // Clear selected vehicle if it's the one being removed
      if (state.selectedVehicle?.plaque_immatriculation === action.payload) {
        state.selectedVehicle = null;
      }
      state.error = null;
    },

    // Set selected vehicle
    setSelectedVehicle: (state, action: PayloadAction<Vehicle | null>) => {
      state.selectedVehicle = action.payload;
      state.error = null;
    },

    // Set vehicle types
    setVehicleTypes: (state, action: PayloadAction<VehicleType[]>) => {
      state.vehicleTypes = action.payload;
      state.error = null;
    },

    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Set error
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },

    // Clear error
    clearError: (state) => {
      state.error = null;
    },

    // Reset state
    resetVehicleState: (state) => {
      state.vehicles = [];
      state.selectedVehicle = null;
      state.vehicleTypes = [];
      state.isLoading = false;
      state.error = null;
    },
  },
});

// Export actions
export const {
  setVehicles,
  addVehicle,
  updateVehicle,
  removeVehicle,
  setSelectedVehicle,
  setVehicleTypes,
  setLoading,
  setError,
  clearError,
  resetVehicleState,
} = vehicleSlice.actions;

// Export reducer
export default vehicleSlice.reducer;

// Selectors
export const selectVehicles = (state: { vehicles: VehicleState }) =>
  state.vehicles.vehicles;

export const selectSelectedVehicle = (state: { vehicles: VehicleState }) =>
  state.vehicles.selectedVehicle;

export const selectVehicleTypes = (state: { vehicles: VehicleState }) =>
  state.vehicles.vehicleTypes;

export const selectVehicleLoading = (state: { vehicles: VehicleState }) =>
  state.vehicles.isLoading;

export const selectVehicleError = (state: { vehicles: VehicleState }) =>
  state.vehicles.error;

// Selector to get vehicle by plaque
export const selectVehicleByPlaque = (plaque: string) => (state: { vehicles: VehicleState }) =>
  state.vehicles.vehicles.find(v => v.plaque_immatriculation === plaque);

// Selector to get vehicles by tax status
export const selectVehiclesByStatus = (status: Vehicle['tax_status']) => (state: { vehicles: VehicleState }) =>
  state.vehicles.vehicles.filter(v => v.tax_status === status);

// Selector to count vehicles by status
export const selectVehicleCountByStatus = (state: { vehicles: VehicleState }) => {
  const vehicles = state.vehicles.vehicles;
  return {
    total: vehicles.length,
    paid: vehicles.filter(v => v.tax_status === 'PAYE').length,
    unpaid: vehicles.filter(v => v.tax_status === 'IMPAYE').length,
    expired: vehicles.filter(v => v.tax_status === 'EXPIRE').length,
    exempt: vehicles.filter(v => v.tax_status === 'EXONERE').length,
  };
};
