import React, { useEffect, useState } from "react";
import { useRouter } from "expo-router";
import {
  SafeAreaView,
  Text,
  Button,
  FlatList,
  TouchableOpacity,
  View,
  Alert,
} from "react-native";
import axios from "axios";
import { socket } from "@/utils/sockets";
import { Player } from "../../types";
import { backendUrl } from "@/utils/config";
import { useLocalSearchParams } from "expo-router";

const WitchKill = () => {
  const router = useRouter();
  const { player: playerString } = useLocalSearchParams() as { player: string };
  const [player, setPlayer] = useState<Player>(JSON.parse(playerString));
  const [playerSelection, setPlayerSelection] = useState<
    { name: string; sid: string }[]
  >([]);

  useEffect(() => {
    if (playerString) {
      setPlayer(JSON.parse(playerString));
    }
  }, [playerString]);

  useEffect(() => {
    const getAllPlayers = async () => {
      try {
        const response = await axios.get(`${backendUrl}/players`);
        const playerData = response.data.players;
        const filteredPlayers = playerData.filter(
          (p: Player) => p.role !== "witch",
        );
        setPlayerSelection(filteredPlayers);
      } catch (error) {
        console.error(error);
      }
    };

    if (player) {
      getAllPlayers();
    }
  }, [player]);

  const handleWitchKill = (sid: string, name: string) => {
    socket.emit("witch_kill_victim", { sid, name });
    router.push({
      pathname: "/(tabs)/GameInterface",
      params: { player: JSON.stringify(player) },
    });
  };

  const handleNoKill = () => {
    router.push({
      pathname: "/(tabs)/GameInterface",
      params: { player: JSON.stringify(player) },
    });
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => (
    <View className="flex-row justify-between items-center p-2 bg-white my-1 rounded-lg">
      <Text className="text-lg">{item.name}</Text>
      <Button
        title="Kill"
        onPress={() => handleWitchKill(item.sid, item.name)}
      />
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-gray-900 p-4">
      <Text className="text-white text-center text-2xl mb-4">
        Choose a player to kill:
      </Text>
      {playerSelection && (
        <FlatList
          data={playerSelection}
          renderItem={renderPlayer}
          keyExtractor={(item) => item.sid}
          className="text-white"
        />
      )}
    </SafeAreaView>
  );
};

export default WitchKill;
