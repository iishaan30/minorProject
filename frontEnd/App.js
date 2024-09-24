import React, { useState, useEffect, useRef } from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { Camera, CameraType } from 'expo-camera/legacy';
import * as ImageManipulator from 'expo-image-manipulator';
import axios from 'axios';

const App = () => {
  const [hasPermission, setHasPermission] = useState(null);
  const [objectName, setObjectName] = useState('');
  const [type, setType] = useState(CameraType.back);
  const cameraRef = useRef(null);

  useEffect(() => {
    const requestPermission = async () => {
      try {
        const { status } = await Camera.requestCameraPermissionsAsync();
        setHasPermission(status === 'granted');
      } catch (error) {
        console.error('Error requesting camera permissions:', error);
        setHasPermission(false);
      }
    };

    requestPermission();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      captureFrame();
    }, 1500); // Capture frame every 1.5 seconds for better performance

    return () => clearInterval(interval);
  }, []);

  const preprocessImage = async (photoUri) => {
    try {
      // Resize image to match the target size
      const manipResult = await ImageManipulator.manipulateAsync(
        photoUri,
        [{ resize: { width: 224, height: 224 } }], // Resize to match model input size
        { base64: true }
      );
      
      // Return the base64 string of the resized image
      return manipResult.base64;
    } catch (error) {
      console.error('Error preprocessing image:', error);
      return null;
    }
  };

  const captureFrame = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          base64: true,
          skipProcessing: true,
        });

        const preprocessedImage = await preprocessImage(photo.uri);

        if (preprocessedImage) {
          const response = await axios.post('http://127.0.0.1:5000/identify', 
            { image: preprocessedImage }, 
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );

          setObjectName(response.data.prediction);
        }
      } catch (error) {
        console.log(error)
        console.error('Error capturing or identifying object:', error.message);
        if (error.response) {
          console.error('Response data:', error.response.data);
        }
      }
    }
  };

  if (hasPermission === null) {
    return <View />;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }
  
  return (
    <View style={styles.container}>
      <Camera
        style={styles.camera}
        ref={cameraRef}
        type={type}
        autoFocus={Camera.Constants.AutoFocus.on}
      />
      <View style={styles.overlay}>
        <Text style={styles.text}>{objectName}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    bottom: 50,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  text: {
    fontSize: 24,
    color: 'white',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    padding: 10,
    borderRadius: 5,
  },
});

export default App;
