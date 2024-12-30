import axios from "axios";
import { useState, useEffect } from "react";
import { Link, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { View, Text, TextInput, Button, ImageBackground } from "react-native";
import { Player } from "../../types";
import { socket } from "@/utils/sockets.js";

import "../../global.css";

export default function HomeScreen() {
  const router = useRouter();
  const [name, setName] = useState("");

  const handleJoinGame = () => {
    socket.emit("add_player", { name });
    socket.on("player_data", (playerData) => {
      router.push({
        pathname: "/(tabs)/waiting-room",
        params: { player: JSON.stringify(playerData) },
      });
    });
  };

  return (
    <ImageBackground
      source={require("../../assets/images/background-app-3.jpeg")}
      className="flex-1"
    >
      <SafeAreaView className="flex-1 justify-end pb-24 items-center">
        <View className="w-4/5 items-center bg-opacity-50 p-5 rounded-lg">
          <Text className="text-2xl text-white mb-5">Werewolf Game</Text>
          <TextInput
            className="w-full p-2 border border-gray-400 rounded mb-5 bg-white"
            placeholder="Enter your name"
            value={name}
            onChangeText={setName}
          />
          <Button title="Join Game" onPress={handleJoinGame} />
        </View>
      </SafeAreaView>
    </ImageBackground>
  );
}
