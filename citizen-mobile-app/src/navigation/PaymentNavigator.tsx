import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { PaymentStackParamList } from '../types/navigation';
import { PaymentMethodScreen } from '../screens/payments';
import { PaymentProcessingScreen } from '../screens/payments';
import { PaymentSuccessScreen } from '../screens/payments';
import { PaymentHistoryScreen } from '../screens/payments';
import { QRCodeViewerScreen } from '../screens/payments/QRCodeViewerScreen';

const PaymentStack = createNativeStackNavigator<PaymentStackParamList>();

export const PaymentNavigator: React.FC = () => {
  return (
    <PaymentStack.Navigator>
      <PaymentStack.Screen 
        name="PaymentHistory" 
        component={PaymentHistoryScreen}
        options={{ title: 'Historique des Paiements' }}
      />
      <PaymentStack.Screen 
        name="PaymentMethod" 
        component={PaymentMethodScreen}
        options={{ title: 'Méthode de Paiement' }}
      />
      <PaymentStack.Screen 
        name="PaymentProcessing" 
        component={PaymentProcessingScreen}
        options={{ title: 'Traitement du Paiement' }}
      />
      <PaymentStack.Screen 
        name="PaymentSuccess" 
        component={PaymentSuccessScreen}
        options={{ title: 'Paiement Réussi', headerBackVisible: false }}
      />
      <PaymentStack.Screen 
        name="QRCodeViewer"
        component={QRCodeViewerScreen}
        options={{ title: 'Code QR', headerBackVisible: true }}
      />
    </PaymentStack.Navigator>
  );
};

export default PaymentNavigator;