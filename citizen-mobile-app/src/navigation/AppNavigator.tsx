import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { RootStackParamList, MainTabParamList } from '../types/navigation';
import { selectIsAuthenticated } from '../store/slices/authSlice';
import { AuthNavigator } from './AuthNavigator';
import { ProfileNavigator } from './ProfileNavigator';
import { VehicleNavigator } from './VehicleNavigator';
import { PaymentNavigator } from './PaymentNavigator';
import { useTranslation } from 'react-i18next';
import { colors } from '../theme/colors';
import { DashboardScreen } from '../screens/dashboard';
import { NotificationsScreen } from '../screens/notifications';

const RootStack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

// Placeholder screens for other tabs
const ScannerScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>Scanner Screen</Text>
  </View>
);

// Main Tab Navigator
const MainTabNavigator: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          switch (route.name) {
            case 'Dashboard':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Vehicles':
              iconName = focused ? 'car' : 'car-outline';
              break;
            case 'Scanner':
              iconName = focused ? 'qr-code' : 'qr-code-outline';
              break;
            case 'Notifications':
              iconName = focused ? 'notifications' : 'notifications-outline';
              break;
            case 'Profile':
              iconName = focused ? 'person' : 'person-outline';
              break;
            default:
              iconName = 'home';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.text.secondary,
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopWidth: 1,
          borderTopColor: colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: t('navigation.dashboard') }}
      />
      <Tab.Screen 
        name="Vehicles" 
        component={VehicleNavigator}
        options={{ title: t('navigation.vehicles'), headerShown: false }}
      />
      <Tab.Screen 
        name="Scanner" 
        component={ScannerScreen}
        options={{ title: t('navigation.scanner') }}
      />
      <Tab.Screen 
        name="Notifications" 
        component={NotificationsScreen}
        options={{ title: t('navigation.notifications') }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileNavigator}
        options={{ title: t('navigation.profile'), headerShown: false }}
      />
    </Tab.Navigator>
  );
};

// Main App Navigator
export const AppNavigator: React.FC = () => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Add any initialization logic here (like checking for stored auth tokens)
    const initializeApp = async () => {
      // Simulate loading time for initialization
      setTimeout(() => {
        setIsLoading(false);
      }, 1000);
    };

    initializeApp();
  }, []);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <RootStack.Screen name="Main" component={MainTabNavigator} />
        ) : (
          <RootStack.Screen name="Auth" component={AuthNavigator} />
        )}
        {/* Additional stacks can be added here for navigation from other screens */}
        <RootStack.Screen name="VehicleStack" component={VehicleNavigator} />
        <RootStack.Screen name="PaymentStack" component={PaymentNavigator} />
      </RootStack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;