import { View, StyleSheet } from 'react-native';
import { Link, Stack } from 'expo-router';

/*
    A page for any invalid urls
*/

export default function NotFoundScreen() {
    return (
        <>
            <Stack.Screen options={{ title: 'Oops! Not Found' }} />
            <View style={styles.container}>
                <Link href="/" style={styles.button}>
                    Go back to Home screen! {/* Button to navigate to the home tab. */}
                </Link>
            </View>
        </>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#05151c',
        justifyContent: 'center',
        alignItems: 'center',
    },

    button: {
        fontSize: 20,
        textDecorationLine: 'underline',
        color: '#fff',
    },
});
