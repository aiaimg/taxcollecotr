import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import { useAuth } from '../context/AuthContext';
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import ScannerScreen from '../screens/ScannerScreen';
import ScanHistoryScreen from '../screens/ScanHistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ScanDetailScreen from '../screens/ScanDetailScreen';
import ContraventionListScreen from '../screens/ContraventionListScreen';
import ContraventionDetailScreen from '../screens/ContraventionDetailScreen';
import ContraventionFormScreen from '../screens/ContraventionFormScreen';
import { AgentType } from '../types/auth.types';

export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
  Scanner: undefined;
  ScanHistory: undefined;
  Profile: undefined;
  ScanDetail: { scan: any };
  ContraventionDetail: { id: string };
  ContraventionForm: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();

function MainTabNavigator() {
  const { agent } = useAuth();
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          switch (route.name) {
            case 'Dashboard':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Scanner':
              iconName = focused ? 'qr-code' : 'qr-code-outline';
              break;
            case 'History':
              iconName = focused ? 'time' : 'time-outline';
              break;
            case 'Profile':
              iconName = focused ? 'person' : 'person-outline';
              break;
            default:
              iconName = 'home-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopWidth: 1,
          borderTopColor: '#e0e0e0',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          headerShown: false,
        }}
      />
      <Tab.Screen
        name="Scanner"
        component={ScannerScreen}
        options={{
          headerShown: false,
        }}
      />
      {agent?.type === AgentType.GOVERNMENT && (
        <Tab.Screen
          name="Contraventions"
          component={ContraventionListScreen}
          options={{
            headerShown: false,
          }}
        />
      )}
      <Tab.Screen
        name="History"
        component={ScanHistoryScreen}
        options={{
          headerShown: false,
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          headerShown: false,
        }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { isAuthenticated } = useAuth();

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: 'white',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {!isAuthenticated ? (
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{
              headerShown: false,
            }}
          />
        ) : (
          <>
            <Stack.Screen
              name="Main"
              component={MainTabNavigator}
              options={{
                headerShown: false,
              }}
            />
            <Stack.Screen
              name="ScanDetail"
              component={ScanDetailScreen}
              options={{
                title: 'Scan Details',
              }}
            />
            <Stack.Screen
              name="ContraventionDetail"
              component={ContraventionDetailScreen}
              options={{
                title: 'Contravention',
              }}
            />
            <Stack.Screen
              name="ContraventionForm"
              component={ContraventionFormScreen}
              options={{
                title: 'New Contravention',
              }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
