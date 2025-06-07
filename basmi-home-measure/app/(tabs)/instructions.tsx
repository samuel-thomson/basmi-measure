import { Text, View, StyleSheet } from "react-native";

export default function AboutScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.heading}>Tragus to Wall</Text>
            <Text style={styles.text}>
                Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall.
                Feet should be hip width apart and parallel. With head in neutral position, patient draws chin in as far as possible.
                Examiner measures tragus to wall. This is repeated on the left and right.
            </Text>
            <Text style={styles.text}></Text>
            <Text style={styles.heading}>Lumbar Side Flexion</Text>
            <Text style={styles.text}>
                Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall.
                Feet should be hip width apart and parallel. Examiner measures the distance from tip of middle finger to floor.
            </Text>
            <Text style={styles.text}>
                Patient reaches towards the floor by side flexing (sliding hand down outside of leg as far as possible).
                Examiner measures the tip of middle finger to floor again and calculates the difference. This is repeated on the left and right.
            </Text>
            <Text style={styles.text}></Text>
            <Text style={styles.heading}>Lumbar Flexion (Modified)</Text>
            <Text style={styles.text}>
                Patient stands with back to wall, their knees straight and shoulder blades, buttocks, and heels against the wall.
                Feet should be hip width apart and parallel. Examiner measures the distance from tip of middle finger to floor.
            </Text>
            <Text style={styles.text}>
                Patient bends forward, keeping knees straight. Examiner measures the tip of middle finger to floor again and calculates the difference.
                This is repeated on the left and right.
            </Text>
            <Text style={styles.text}></Text>
            <Text style={styles.heading}>Cervical Rotation</Text>
            <Text style={styles.text}>
                Patient lies on floor, with their forehead horizontal and head in neutral position. Examiner uses a goniometer or inclinometer to measure.
                Patient rotates head as far as possible, keeping shoulders still. Examiner measures the rotation. This is measured on both sides.
            </Text>
            <Text style={styles.text}></Text>
            <Text style={styles.heading}>Intermalleolar Distance</Text>
            <Text style={styles.text}>
                Patient lies on the floor. Keeping knees straight and legs in contact with the floor, patient takes legs as far apart as possible.
                Examiner measures the distance between the medial malleoli (inner ankles).
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#05151c',
        alignItems: 'center',
        justifyContent: 'center',
    },
    text: {
        color: '#fff',
    },
    heading: {
        color: '#fff',
        fontWeight: 'bold',
    }
});