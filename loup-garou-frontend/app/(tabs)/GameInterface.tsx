import { Text, View, TouchableOpacity, Button } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useState, useEffect } from "react";
import { Player } from "../../types";
import { getRoleDescription } from "../../constants/roles";
import { socket } from "@/utils/sockets.js";

const GameInterface: React.FC = () => {
  const router = useRouter();

  const { player: playerString } = useLocalSearchParams() as { player: string };
  const player: Player = JSON.parse(playerString);

  const [showDescription, setShowDescription] = useState(false);
  //const [showCupidon, setShowCupidon] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);

  const handleCardPress = () => {
    setShowDescription(!showDescription);
  };

  useEffect(() => {
    setGameStarted(true);
    socket.emit("start_game");
  }, []);

  useEffect(() => {
    console.log("The game has started: ", gameStarted);
    if (gameStarted) {
      console.log("checking for cupidon choice");
      socket.once("cupidon_choice", (data) => {
        router.push("/(tabs)/Cupidon");
      });

      return () => {
        socket.off("cupidon_choice");
      };
    }
  }, [gameStarted]);

  return (
    <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
      <Text className="text-white text-2xl mb-5">Game Interface</Text>
      <Text className="text-white text-lg mb-2">Player: {player.name}</Text>
      <Text className="text-white text-lg mb-5">Role: {player.role}</Text>
      <TouchableOpacity onPress={handleCardPress}>
        <View className="w-72 h-96 bg-white rounded-lg items-center justify-center shadow-lg">
          {showDescription ? (
            <Text className="text-black text-lg text-center p-5">
              {getRoleDescription(player.role)}
            </Text>
          ) : (
            <Text className="text-black text-lg text-center p-5">
              Tap to reveal role description
            </Text>
          )}
        </View>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

export default GameInterface;
