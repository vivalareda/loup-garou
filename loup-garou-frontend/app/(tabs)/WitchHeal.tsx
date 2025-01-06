import React from "react";
import { SafeAreaView, Text, Button, Modal, View } from "react-native";
import { useState, useEffect } from "react";
import { socket } from "@/utils/sockets.js";

const WitchHeal = ({
  visible,
  victim,
  onClose,
}: {
  visible: boolean;
  victim: string;
  onClose: () => void;
}) => {
  const handleChoice = (choice: string) => {
    choice === "yes"
      ? socket.emit("witch_heal_victim")
      : socket.emit("witch_no_heal");
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide">
      <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
        <View className="w-80 h-96 bg-white rounded-lg items-center justify-center shadow-lg p-5">
          <Text className="text-black text-2xl mb-5">Guérison</Text>
          <Text className="text-black text-lg mb-2">
            Les loup-garous ont tué {victim}! Voulez-vous utiliser votre pouvoir
            de guérison?
          </Text>
          <View className="flex flex-row justify-between w-full">
            <Button title="Oui" onPress={() => handleChoice("yes")} />
            <Button title="Non" onPress={() => handleChoice("no")} />
          </View>
        </View>
      </SafeAreaView>
    </Modal>
  );
};

export default WitchHeal;
