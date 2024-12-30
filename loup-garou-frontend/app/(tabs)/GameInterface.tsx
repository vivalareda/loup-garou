import { Text, View, TouchableOpacity, Button } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useState, useEffect } from "react";
import { Player } from "../../types";
import { getRoleDescription } from "../../constants/roles";
import { socket } from "@/utils/sockets.js";
import Cupidon from "./Cupidon";
import LoveAlert from "./LoveAlert";

const GameInterface: React.FC = () => {
  const router = useRouter();
  const [player, setPlayer] = useState<Player | null>(null);
  const [showDescription, setShowDescription] = useState(false);
  const [showCupidon, setShowCupidon] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  const [isInLove, setIsInLove] = useState(false);
  const [loverName, setLoverName] = useState("");

  const { player: playerString } = useLocalSearchParams() as { player: string };

  const handleCardPress = () => {
    setShowDescription(!showDescription);
  };

  useEffect(() => {
    setPlayer(JSON.parse(playerString));
  }, []);

  useEffect(() => {
    const handleCupidonChoice = () => {
      setShowCupidon(true);
    };

    socket.once("cupidon_choice", handleCupidonChoice);

    return () => {
      socket.off("cupidon_choice");
    };
  }, []);

  useEffect(() => {
    const handleIsInLove = (data: { lover: string }) => {
      console.log(data.lover);
      setIsInLove(true);
      console.log("Set player in love");
      setLoverName(data.lover);
      console.log("Set lover name");
    };

    socket.once("alert_lovers", handleIsInLove);

    return () => {
      socket.off("alert_lovers");
    };
  }, []);

  return (
    <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
      <Text className="text-white text-2xl mb-5">Game Interface</Text>
      <Text className="text-white text-lg mb-2">Player: {player?.name}</Text>
      <Text className="text-white text-lg mb-5">Role: {player?.role}</Text>
      <TouchableOpacity onPress={handleCardPress}>
        <View className="w-72 h-96 bg-white rounded-lg items-center justify-center shadow-lg">
          {loverName && (
            <LoveAlert
              visible={isInLove}
              onClose={() => setIsInLove(false)}
              loverName={loverName}
            />
          )}
          {player && (
            <Cupidon
              visible={showCupidon}
              onClose={() => setShowCupidon(false)}
              cupidonName={player.name}
            />
          )}
          {showDescription ? (
            <Text className="text-black text-lg text-center p-5">
              {player?.role ? getRoleDescription(player.role) : ""}
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
