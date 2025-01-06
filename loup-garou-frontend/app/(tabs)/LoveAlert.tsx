import React from "react";
import { SafeAreaView, Text, Button, Modal, View } from "react-native";
import { useState, useEffect } from "react";
import { socket } from "@/utils/sockets.js";

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
        <View className="w-72 h-96 bg-white rounded-lg items-center justify-center shadow-lg p-5">
          <Text className="text-black text-2xl mb-5">Love Alert</Text>
          <Text className="text-black text-lg mb-2">
            Vous etes en couple avec {loverName}!
          </Text>
          <Button title="Close" onPress={onClose} disabled={isDisabled} />
        </View>
      </SafeAreaView>
    </Modal>
  );
};

export default LoveAlert;
