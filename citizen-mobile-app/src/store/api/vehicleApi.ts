import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { API_BASE_URL } from '../../utils/constants';
import type { RootState } from '../store';
import type {
  Vehicle,
  VehicleType,
  VehicleFormData,
  TaxInfo,
} from '../../types/models';

/**
 * RTK Query API for vehicle management
 * Provides endpoints for CRUD operations on vehicles and vehicle types
 */
export const vehicleApi = createApi({
  reducerPath: 'vehicleApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.tokens?.access;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Vehicle', 'VehicleType'],
  keepUnusedDataFor: 300, // 5 minutes cache for vehicles
  endpoints: (builder) => ({
    // Get list of vehicles
    getVehicles: builder.query<Vehicle[], void>({
      query: () => '/api/v1/vehicles/',
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Vehicle' as const, id })),
              { type: 'Vehicle', id: 'LIST' },
            ]
          : [{ type: 'Vehicle', id: 'LIST' }],
    }),

    // Get vehicle by plaque
    getVehicle: builder.query<Vehicle, string>({
      query: (plaque) => `/api/v1/vehicles/${plaque}/`,
      providesTags: (result, error, plaque) => [{ type: 'Vehicle', id: plaque }],
    }),

    // Get vehicle tax info
    getVehicleTaxInfo: builder.query<TaxInfo, string>({
      query: (plaque) => `/api/v1/vehicles/${plaque}/tax_info/`,
    }),

    // Create new vehicle
    createVehicle: builder.mutation<Vehicle, FormData>({
      query: (formData) => ({
        url: '/api/v1/vehicles/',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: [{ type: 'Vehicle', id: 'LIST' }],
    }),

    // Update vehicle
    updateVehicle: builder.mutation<Vehicle, { plaque: string; data: FormData }>({
      query: ({ plaque, data }) => ({
        url: `/api/v1/vehicles/${plaque}/`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { plaque }) => [
        { type: 'Vehicle', id: plaque },
        { type: 'Vehicle', id: 'LIST' },
      ],
    }),

    // Delete vehicle
    deleteVehicle: builder.mutation<void, string>({
      query: (plaque) => ({
        url: `/api/v1/vehicles/${plaque}/`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'Vehicle', id: 'LIST' }],
    }),

    // Get vehicle types
    getVehicleTypes: builder.query<VehicleType[], void>({
      query: () => '/api/v1/vehicle-types/',
      providesTags: [{ type: 'VehicleType', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetVehiclesQuery,
  useGetVehicleQuery,
  useGetVehicleTaxInfoQuery,
  useCreateVehicleMutation,
  useUpdateVehicleMutation,
  useDeleteVehicleMutation,
  useGetVehicleTypesQuery,
} = vehicleApi;
