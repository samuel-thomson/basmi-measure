import { CameraView, CameraType, useCameraPermissions} from 'expo-camera';
import { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import {useIsFocused} from "@react-navigation/core";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRef } from "react";
import { useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

/*
    Measuring tab
*/


export default function MeasureScreen() {
    const { value } = useLocalSearchParams();
    console.log(value);
    const index = Number(value); // convert to number if needed

    const [facing, setFacing] = useState<CameraType>('back');
    const [permission, requestPermission] = useCameraPermissions();
    const isFocused = useIsFocused();
    const cameraRef = useRef<CameraView| null>(null);

    const [isFirstPhotoTaken, setIsFirstPhotoTaken] = useState(false);
    const [firstPhotoData, setFirstPhotoData] = useState<any>(null);

    const storeData = async(key: string, value: string) => {
        try {
            await AsyncStorage.setItem(key, value);
        } catch (error) {
            console.error(error);
        }
    }

    /*
        Arrays to change the content and paths based on parameter value from the index page.
    */

    const instructions: string[] = [
        "Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall. Feet should be hip width apart and parallel. With head in neutral position, patient draws chin in as far as possible. Take a full body photo of the patient from their left side.",
        "Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall. Feet should be hip width apart and parallel. With head in neutral position, patient draws chin in as far as possible. Take a full body photo of the patient from their right side.",
        "Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall. Feet should be hip width apart and parallel, and hands to their side. Take a full body photo of the patient head on.",
        "Patient reaches towards the floor with their left hand relaxed by side flexing (sliding left hand down outside of leg as far as possible). Take a full body photo of the patient head on.",
        "Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall. Feet should be hip width apart and parallel, and hands to their side. Take a full body photo of the patient head on.",
        "Patient reaches towards the floor with their right hand relaxed by side flexing (sliding right hand down outside of leg as far as possible). Take a full body photo of the patient head on.",
        "Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall. Feet should be hip width apart and parallel, and hands to their side. Take a full body photo of the patient head on.",
        "Patient bends forward, keeping knees straight. Take a full body photo of the patient head on.",
       "Patient lies on the floor, on their back. Their forehand should be horizontal and head in neutral position. Take a full body photo of the patient head on.",
        "Patient rotates head as far as possible to the left, keeping shoulders still. Take a full body photo of the patient head on.",
        "Patient lies on the floor, on their back. Their forehand should be horizontal and head in neutral position. Take a full body photo of the patient head on.",
        "Patient rotates head as far as possible to the right, keeping shoulders still. Take a full body photo of the patient head on.",
        "Patient lies on the floor, on their back. Keeping knees straight and legs in contact with the floor, patient takes legs as far apart as possible. Take a full body photo of the patient head on."
    ]
    const addresses: string[] = [
        "http://192.168.0.179:8000/tragusleft", //192.168.1.138
        "http://192.168.0.179:8000/tragusright",
        "http://192.168.0.179:8000/flexionleft", //sideleft
        "http://192.168.0.179:8000/flexionleft",
        "http://192.168.0.179:8000/rights",
        "http://192.168.0.179:8000/rights",
        "http://192.168.0.179:8000/lumbar",
        "http://192.168.0.179:8000/lumbar",
        "http://192.168.0.179:8000/cervicalleft",
        "http://192.168.0.179:8000/cervicalleft",
        "http://192.168.0.179:8000/cright",
        "http://192.168.0.179:8000/cright",
        "http://192.168.0.179:8000/intermalleolar"
    ];
    const measurements: string[] = [
        "tragus-left",
        "tragus-right",
        "side-left",
        "side-left",
        "side-right",
        "side-right",
        "lumbar-left",
        "lumbar-right",
        "cervical-left",
        "cervical-left",
        "cervical-right",
        "cervical-right",
        "intermalleolar"
    ]

    /*
        Sets the instruction message displayed at the bottom of the screen
    */

    const [message, setMessage] = useState<string>(instructions[index]);

    /*
        Sets up camera flex box.
    */

    console.log("Index", index);
    if (!permission) {
        // Camera permissions are still loading.
        return <View/>;
    }

    if (!permission.granted) {
        // Camera permissions are not granted yet.
        return (
            <View style={styles.container}>
                <Text style={styles.message}>We need your permission to show the camera</Text>
                <Button onPress={requestPermission} title="grant permission"/>
            </View>
        );
    }

    function toggleCameraFacing() {
        setFacing(current => (current === 'back' ? 'front' : 'back'));
    }

    /*
        Takes a photo and sends the image data to the FastAPI server - handles measurements which require two images
    */

    const takePhoto = async() => {
        if (!cameraRef.current) return;

        const options = { quality: 0.7, base64: true};

        if (index === 0 || index === 1 || index === 12) {
            console.log("Taking first photo...");
            const data = await cameraRef.current.takePictureAsync(options);
            const imageData = data?.base64;

            try {
                const response = await fetch(addresses[index], {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image: imageData,
                    })
                });

                const responseJson = await response.json();
                console.log("Image sent successfully", responseJson);
                storeData(measurements[index], JSON.stringify(responseJson['result']));
                setMessage(responseJson['result']);
            } catch (error) {
                console.error("Error sending image:", error);
            }
        } else {
            if (!isFirstPhotoTaken){
                console.log("Taking first photo...");
                const firstPhoto = await cameraRef.current.takePictureAsync(options);
                setFirstPhotoData(firstPhoto);
                setIsFirstPhotoTaken(true);
                setMessage(instructions[index+1]);
            } else {
                console.log("Taking second photo...");
                const secondPhoto = await cameraRef.current.takePictureAsync(options);
                try {
                    const response = await fetch(addresses[index], {
                        method: "POST",
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            image1: firstPhotoData?.base64,
                            image2: secondPhoto?.base64,
                        })
                    });

                    const responseJson = await response.json();
                    console.log("Two images sent successfully", responseJson);
                    if (index == 6){
                        storeData(measurements[index], JSON.stringify(responseJson['result'][0]));
                        storeData(measurements[index+1], JSON.stringify(responseJson['result'][1]));
                    } else{
                        storeData(measurements[index], JSON.stringify(responseJson['result']));
                    }
                    setMessage(responseJson['result']);
                } catch (error) {
                    console.error("Error sending two images:", error);
                }
                setIsFirstPhotoTaken(false);
                setFirstPhotoData(null);
            }
        }

    }

    return (
        <View style={styles.container}>
            { isFocused && <CameraView ref={cameraRef} style={styles.camera} facing={facing}>
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.button} onPress={takePhoto}>
                        <Ionicons name={'camera'} color={'#89CFF0'} size={50}/>
                    </TouchableOpacity>
                </View>
            </CameraView>}
            <View style={styles.instructionsContainer}>
                <Text style={styles.instructionsText}>
                    {message}
                </Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#05151c',
        justifyContent: 'center',
    },
    instructionsContainer: {
        flex: 2,
        backgroundColor: '#89CFF0',
        maxHeight: '20%',
        padding: 15,
    },
    instructionsText: {
        color: '#05151c',
        fontSize: 16,
    },
    message: {
        textAlign: 'center',
        paddingBottom: 10,
    },
    camera: {
        flex: 1,
    },
    buttonContainer: {
        flex: 1,
        flexDirection: 'row',
        backgroundColor: 'transparent',
        margin: 20,
    },
    button: {
        flex: 1,
        alignSelf: 'flex-end',
        alignItems: 'center',
    },
    text: {
        fontSize: 24,
        fontWeight: 'bold',
        color: 'white',
    },
});
