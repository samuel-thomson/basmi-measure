import { Tabs } from 'expo-router';
import Ionicons from '@expo/vector-icons/Ionicons';


export default function TabLayout() {
    return (
        <Tabs
            screenOptions={{
                tabBarActiveTintColor: '#89CFF0',
                headerStyle: {
                    backgroundColor: '#05151c',
                },
                headerShadowVisible: false,
                headerTintColor: '#89CFF0',
                tabBarStyle: {
                    backgroundColor: '#05151c',
                },
            }}
        >
            <Tabs.Screen
                name="index"
                options={{
                    title: 'Home',
                    tabBarIcon: ({ color, focused }) => (
                        <Ionicons name={focused ? 'home-sharp' : 'home-outline'} color={color} size={24} />
                    ),
                }}
            />
            <Tabs.Screen
                name="results"
                options={{
                    title: 'Results',
                    tabBarIcon: ({ color, focused }) => (
                        <Ionicons name={focused ? 'bar-chart-sharp' : 'bar-chart-outline'} color={color} size={24}/>
                    ),
                }}
            />
            <Tabs.Screen
                name="instructions"
                options={{
                    title: 'Manual Instructions',
                    tabBarIcon: ({ color, focused }) => (
                        <Ionicons name={focused ? 'information-circle-sharp' : 'information-circle-outline'} color={color} size={24}/>
                    ),
                }}
            />
        </Tabs>
    );
}
