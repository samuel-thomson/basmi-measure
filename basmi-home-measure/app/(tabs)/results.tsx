import {Text, View, StyleSheet, TouchableOpacity} from "react-native";
import { Link } from 'expo-router';
import {CameraView} from "expo-camera";
import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { useEffect, useState } from "react";
import { useFocusEffect } from '@react-navigation/native';

/*
    Results page menu updates when a new BASMI measurement is taken.
*/

export default function Index() {
    const [results, setResults] = useState<number[]>(Array(13).fill(0));

    const getData = async () => {
        const newResults = [...results];

        newResults[0] = Number(await AsyncStorage.getItem("tragus-left")) || 0;
        newResults[1] = Number(await AsyncStorage.getItem("tragus-right")) || 0;
        const sl_value = Number(await AsyncStorage.getItem("side-left")) || 0;
        newResults[2] = sl_value;
        newResults[3] = sl_value;
        const sr_value = Number(await AsyncStorage.getItem("side-right")) || 0;
        newResults[4] = sr_value;
        newResults[5] = sr_value;
        newResults[6] = Number(await AsyncStorage.getItem("lumbar-left")) || 0;
        newResults[7] = Number(await AsyncStorage.getItem("lumbar-right")) || 0;
        const cl_value = Number(await AsyncStorage.getItem("cervical-left")) || 0;
        newResults[8] = cl_value;
        newResults[9] = cl_value;
        const cr_value = Number(await AsyncStorage.getItem("cervical-right")) || 0;
        newResults[10] = cr_value;
        newResults[11] = cr_value;
        newResults[12] = Number(await AsyncStorage.getItem("intermalleolar")) || 0;

        setResults(newResults);
    };


    // Fetch data when screen is focused (better for tab navigation)
    useFocusEffect(
        React.useCallback(() => {
            getData();
        }, [])
    );

    return (
        <View style={styles.container}>
            <View style={styles.titleContainer}>
                <Text style={styles.title}>Tragus to Wall</Text>
            </View>
            <View style={styles.resultRow}>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Left: " + results[0] + " cm"}</Text>
                </View>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Right: " + results[1] + " cm"}</Text>
                </View>
            </View>
    
            <View style={styles.titleContainer}>
                <Text style={styles.title}>Side Lumbar Flexion</Text>
            </View>
            <View style={styles.resultRow}>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Left: " + results[2] + " cm"}</Text>
                </View>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Right: " + results[4] + " cm"}</Text>
                </View>
            </View>
    
            <View style={styles.titleContainer}>
                <Text style={styles.title}>Lumbar Flexion (Modified)</Text>
            </View>
            <View style={styles.resultRow}>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Left: " + results[6] + " cm"}</Text>
                </View>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Right: " + results[7] + " cm"}</Text>
                </View>
            </View>
    
            <View style={styles.titleContainer}>
                <Text style={styles.title}>Cervical Rotation</Text>
            </View>
            <View style={styles.resultRow}>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Left: " + results[8] + ' °'}</Text>
                </View>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Right: " + results[10] + ' °'}</Text>
                </View>
            </View>
    
            <View style={styles.titleContainer}>
                <Text style={styles.title}>Intermalleolar Distance</Text>
            </View>
            <View style={styles.resultRow}>
                <View style={styles.resultWrapper}>
                    <Text style={styles.resultText}>{"Right: " + results[12] + " cm"}</Text>
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
        backgroundColor: '#89CFF0',
        //paddingVertical: 10,
        paddingHorizontal: 20,
        //borderRadius: 5,
        marginHorizontal: 10,
        //marginBottom: 15,
        //alignItems: 'center',
        justifyContent: 'center',
        width: '80%',
    },
    title: {
        color: '#05151c',
        fontSize: 16,
    },
    resultRow: {
        flexDirection: "row",
        justifyContent: "center",
        marginTop: 10,
        flexWrap: 'wrap',
        width: '80%',
    },
    resultWrapper: {
        flex: 1,
        marginBottom: 15,
    },
    resultText: {
        color: '#fff',
        fontSize: 20,
        textAlign: 'center',
        marginVertical: 10,
    }
});