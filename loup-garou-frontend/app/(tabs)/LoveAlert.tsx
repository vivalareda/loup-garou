import React from "react";
import {
  TouchableOpacity,
  SafeAreaView,
  Text,
  Modal,
  View,
  StyleSheet,
} from "react-native";
import { useState, useEffect } from "react";
import { socket } from "@/utils/sockets.js";
import LottieView from "lottie-react-native";

const LoveAlert = ({
  visible,
  onClose,
  loverName,
}: {
  visible: boolean;
  onClose: () => void;
  loverName: string;
}) => {
  const [isDisabled, setIsDisabled] = useState(true);

  useEffect(() => {
    socket.on("lover_can_close", () => {
      setIsDisabled(false);
    });
  }, []);

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
        <View className="w-80 bg-white rounded-lg items-center justify-center shadow-lg p-5">
          <Text className="text-black text-2xl font-bold mb-2">Love Alert</Text>
          <Text className="text-black text-lg mt-5 text-center">
            Vous etes en couple avec {loverName}!
          </Text>
          <View className="w-48 h-48 my-5">
            <LottieView
              source={require("../../assets/CupidAnimation.json")}
              style={styles.animation}
              autoPlay
              loop
            />
          </View>
          <TouchableOpacity
            onPress={onClose}
            disabled={isDisabled}
            className={`mt-5 px-4 py-2 rounded ${
              isDisabled ? "bg-gray-400" : "bg-blue-500"
            }`}
          >
            <Text className="text-white text-lg">Close</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  animation: {
    width: "100%",
    height: "100%",
  },
});

export default LoveAlert;
