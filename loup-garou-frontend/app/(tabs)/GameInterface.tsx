import { Text, View, TouchableOpacity, Button } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useState, useEffect } from "react";
import { Player } from "../../types";
import { getRoleDescription } from "../../constants/roles";
import { socket } from "@/utils/sockets.js";
import Cupidon from "./Cupidon";
import LoveAlert from "./LoveAlert";
import * as Haptics from "expo-haptics";

const GameInterface: React.FC = () => {
  const [player, setPlayer] = useState<Player | null>(null);
  const [showDescription, setShowDescription] = useState(false);
  const [showCupidon, setShowCupidon] = useState(false);
  const [isInLove, setIsInLove] = useState(false);
  const [loverName, setLoverName] = useState("");
  const { player: playerString } = useLocalSearchParams() as { player: string };

  const handleCardPress = () => {
    setShowDescription(!showDescription);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
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
      setIsInLove(true);
      setLoverName(data.lover);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
        .then(() => console.log("Haptic feedback triggered"))
        .catch((error) =>
          console.error("Error triggering haptic feedback", error),
        );
    };
    socket.once("alert_lovers", handleIsInLove);
    return () => {
      socket.off("alert_lovers");
    };
  }, []);

  return (
    <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
      <Text className="text-white text-2xl mb-5">Game Interface</Text>
      <Text className="text-white text-lg mb-5">Player: {player?.name}</Text>

      <TouchableOpacity
        onPress={handleCardPress}
        className="active:scale-95 transform transition-all"
      >
        <View className="w-72 h-96 bg-gradient-to-br from-white to-gray-100 rounded-xl items-center justify-between p-6 shadow-xl border border-gray-200">
          <View className="w-full flex items-center">
            {!showDescription ? (
              <>
                <View className="w-16 h-16 bg-gray-900 rounded-full mb-4 items-center justify-center">
                  <Text className="text-white text-2xl">?</Text>
                </View>
                <Text className="text-gray-800 text-lg font-medium text-center">
                  Appuyez sur la carte pour révéler votre rôle
                </Text>
              </>
            ) : (
              <>
                <Text className="text-white text-2xl font-bold mb-4">
                  {player?.role?.toUpperCase()}
                </Text>
                <View className="border-t border-gray-200 w-full pt-4">
                  <Text className="text-gray-400 text-lg text-center leading-relaxed">
                    {player?.role ? getRoleDescription(player.role) : ""}
                  </Text>
                </View>
              </>
            )}
          </View>

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
        </View>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

export default GameInterface;
