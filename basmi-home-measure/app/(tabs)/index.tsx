import {Text, View, StyleSheet, TouchableOpacity} from "react-native";
import { Link } from 'expo-router';
import {CameraView} from "expo-camera";

//npx expo start --tunnel

export default function Index() {
  return (
    <View style={styles.container}>
        <View style={styles.titleContainer}>
            <Text style={styles.title}>Tragus to Wall</Text>
        </View>
        <View style={styles.buttonRow}>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 0 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Left</Text>
                </Link>
            </View>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 1 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Right</Text>
                </Link>
            </View>
        </View>

        <View style={styles.titleContainer}>
            <Text style={styles.title}>Side Lumbar Flexion</Text>
        </View>
        <View style={styles.buttonRow}>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 2 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Left</Text>
                </Link>
            </View>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 4 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Right</Text>
                </Link>
            </View>
        </View>

        <View style={styles.titleContainer}>
            <Text style={styles.title}>Lumbar Flexion (Modified)</Text>
        </View>
        <View style={styles.buttonRow}>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 6 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Measure</Text>
                </Link>
            </View>
        </View>

        <View style={styles.titleContainer}>
            <Text style={styles.title}>Cervical Rotation</Text>
        </View>
        <View style={styles.buttonRow}>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 8 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Left</Text>
                </Link>
            </View>
            <View style={styles.buttonWrapper}>
                <Link href={{ pathname: "/Measuring", params: { value: 10 } }} style={styles.button}>
                    <Text style={styles.buttonText}>Right</Text>
                </Link>
            </View>
        </View>

        <View style={styles.titleContainer}>
            <Text style={styles.title}>Intermalleolar Distance</Text>
        </View>
        <View style={styles.buttonRow}>
            <View style={styles.buttonWrapper}>
                <Link  href={{ pathname: "/Measuring", params: { value: 12 } }}  style={styles.button}>
                    <Text style={styles.buttonText}>Measure</Text>
                </Link>
            </View>
        </View>
    </View>
  );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#05151c',
        alignItems: 'center',
        justifyContent: 'center',
        paddingHorizontal: 10,
        paddingVertical: 20,
    },
    titleContainer: {
        paddingVertical: 10,
        alignItems: 'center',
        borderRadius: 5,
    },
    title: {
        color: '#fff',
        fontSize: 20,
    },
    buttonRow: {
        flexDirection: "row",
        justifyContent: "center",
        marginTop: 10,
        flexWrap: 'wrap',
        width: '80%',
    },
    buttonWrapper: {
      flex: 1,
    },
    button: {
        backgroundColor: '#89CFF0',
        paddingVertical: 10,
        paddingHorizontal: 20,
        borderRadius: 5,
        marginHorizontal: 10,
        marginBottom: 15,
        alignItems: 'center',
        justifyContent: 'center',
    },
    buttonText: {
        color: '#05151c',
        fontSize: 16,
        textAlign: 'center',
    }
});