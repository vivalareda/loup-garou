import { Text, View, TouchableOpacity, Button, Modal } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useState, useEffect } from "react";
import { Player } from "../../types";
import { getRoleDescription } from "../../constants/roles";
import { socket } from "@/utils/sockets.js";
import Cupidon from "@/components/roles/Cupidon";
import Hunter from "@/components/roles/Hunter";
import LoveAlert from "./LoveAlert";
import WitchHeal from "./WitchHeal";
import WitchKill from "./WitchKill";
import * as Haptics from "expo-haptics";

const GameInterface: React.FC = () => {
  const router = useRouter();

  const [player, setPlayer] = useState<Player | null>(null);
  const [showDescription, setShowDescription] = useState(false);
  const [showCupidon, setShowCupidon] = useState(false);
  const [showHunter, setShowHunter] = useState(false);
  const [isInLove, setIsInLove] = useState(false);
  const [loverName, setLoverName] = useState("");
  const [showWitchHeal, setShowWitch] = useState(false);
  const [werewolfTarget, setWerewolfTarget] = useState("");
  const [showWitchKillModal, setShowWitchKillModal] = useState(false);
  const [showWitchKill, setShowWitchKill] = useState(false);

  const { player: playerString } = useLocalSearchParams() as { player: string };

  const handleCardPress = () => {
    setShowDescription(!showDescription);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  useEffect(() => {
    if (playerString) {
      console.log("Player string is", playerString);
      const parsedPlayer: Player = JSON.parse(playerString);
      setPlayer(parsedPlayer);
    }
  }, []);

  useEffect(() => {
    console.log("Werewolf target is", werewolfTarget);
    if (werewolfTarget) {
      console.log("Setting show werewolf to true");
      setShowWitch(true);
    }
  }, [werewolfTarget]);

  useEffect(() => {
    const handleCupidonChoice = () => {
      setShowCupidon(true);
    };

    const handleIsInLove = (data: { lover: string }) => {
      setIsInLove(true);
      setLoverName(data.lover);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
        .then(() => console.log("Haptic feedback triggered"))
        .catch((error) =>
          console.error("Error triggering haptic feedback", error),
        );
    };

    const handleDeath = () => {
      cleanup();
      router.push("/(tabs)/Death");
    };

    const handleSeerChoice = () => {
      router.push("/(tabs)/Seer");
    };

    const handleWitchHeel = (data: { victim: string }) => {
      const victim = data.victim;
      setWerewolfTarget(victim);
    };

    const handleDayVote = () => {
      router.push({
        pathname: "/(tabs)/DayVote",
        params: { player: JSON.stringify(player) },
      });
    };

    const handleWerewolfWakeUp = () => {
      if (player) {
        try {
          router.push({
            pathname: "/(tabs)/Werewolf",
            params: { player: JSON.stringify(player) },
          });
          console.log("Router push completed");
        } catch (error) {
          console.error("Navigation error:", error);
        }
      }
    };
    const handleWitchKill = () => {
      setShowWitchKillModal(true);
    };

    const handleHunterSelection = () => {
      setShowHunter(true);
    };

    const cleanup = () => {
      socket.off("cupidon_choice", handleCupidonChoice);
      socket.off("alert_lovers", handleIsInLove);
      socket.off("witch_heel", handleWitchHeel);
      socket.off("alert_dead", handleDeath);
      socket.off("werewolf_wake_up", handleWerewolfWakeUp);
      socket.off("day_vote", handleDayVote);
      socket.off("witch_kill", handleWitchKill);
      //socket.off("seer_choice", handleSeerChoice);
    };

    socket.once("cupidon_choice", handleCupidonChoice);
    socket.once("alert_lovers", handleIsInLove);
    socket.once("hunter_selection", handleHunterSelection);
    socket.on("witch_heal", handleWitchHeel);
    socket.on("alert_dead", handleDeath);
    socket.on("witch_kill", handleWitchKill);
    socket.on("werewolf_wake_up", handleWerewolfWakeUp);
    socket.on("day_vote", handleDayVote);

    //socket.on("seer_choice", handleSeerChoice);

    return () => {
      cleanup();
    };
  }, [player]);

  useEffect(() => {
    if (player && showWitchKill) {
      try {
        router.push({
          pathname: "/(tabs)/WitchKill",
          params: { player: JSON.stringify(player) },
        });
      } catch (error) {
        console.error("Navigation error:", error);
      }
    }
  }, [showWitchKill]);

  const handleShowWitchKillModal = (choice: string) => {
    if (choice === "yes") {
      setShowWitchKill(true);
      setShowWitchKillModal(false);
    } else {
      setShowWitchKillModal(false);
      socket.emit("witch_no_kill");
    }
  };

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
        </View>

        {loverName && (
          <LoveAlert
            visible={isInLove}
            onClose={() => {
              setIsInLove(false);
              socket.emit("lover_alert_closed");
              socket.emit("lover_alert_closed"); // TODO: Remove this line this is for testing purposes since we only have one player
            }}
            loverName={loverName}
          />
        )}

        {player && (
          <>
            <Cupidon
              visible={showCupidon}
              onClose={() => setShowCupidon(false)}
              cupidonName={player.name}
            />
            <Hunter
              visible={showHunter}
              onClose={() => setShowHunter(false)}
              hunterName={player.name}
            />
            <WitchHeal
              visible={showWitchHeal}
              onClose={() => setShowWitch(false)}
              victim={werewolfTarget}
            />
          </>
        )}
        {showWitchKillModal && (
          <Modal
            visible={showWitchKillModal}
            animationType="slide"
            transparent={true}
            onRequestClose={() => setShowWitchKillModal(false)}
          >
            <View className="flex-1 justify-center items-center bg-gray-50/50 bg-opacity-50">
              <View className="bg-white p-6 rounded-lg shadow-lg w-80">
                <Text className="text-black text-xl mb-4">
                  Voulez-vous tuer quelqu'un?
                </Text>
                <View className="flex-row justify-between">
                  <TouchableOpacity
                    onPress={() => handleShowWitchKillModal("yes")}
                    className="bg-red-500 p-3 rounded-lg"
                  >
                    <Text className="text-white">Oui</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => handleShowWitchKillModal("no")}
                    className="bg-green-500 p-3 rounded-lg"
                  >
                    <Text className="text-white">Non</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </Modal>
        )}
      </TouchableOpacity>
    </SafeAreaView>
  );
};

export default GameInterface;
