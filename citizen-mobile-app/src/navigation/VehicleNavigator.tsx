import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { VehicleStackParamList } from '../types/navigation';
import { VehicleListScreen } from '../screens/vehicles/VehicleListScreen';
import { VehicleDetailScreen } from '../screens/vehicles/VehicleDetailScreen';
import { AddVehicleScreen } from '../screens/vehicles/AddVehicleScreen';

const VehicleStack = createNativeStackNavigator<VehicleStackParamList>();

export const VehicleNavigator: React.FC = () => {
  return (
    <VehicleStack.Navigator>
      <VehicleStack.Screen 
        name="VehicleList" 
        component={VehicleListScreen}
        options={{ title: 'Mes Véhicules' }}
      />
      <VehicleStack.Screen 
        name="VehicleDetail" 
        component={VehicleDetailScreen}
        options={{ title: 'Détails du Véhicule' }}
      />
      <VehicleStack.Screen 
        name="AddVehicle" 
        component={AddVehicleScreen}
        options={{ title: 'Ajouter un Véhicule' }}
      />
    </VehicleStack.Navigator>
  );
};

export default VehicleNavigator;