import { Stack } from "expo-router";

export default function RootLayout() {
  return (
      <Stack
          screenOptions={{
              headerBackTitle: 'Home',
              headerStyle: {
                  backgroundColor: '#05151c',
              },
                  headerTintColor: '#89CFF0',
          }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="+not-found" />
      </Stack>
  );
}
