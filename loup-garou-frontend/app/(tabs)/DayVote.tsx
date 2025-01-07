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

const DayVote = () => {
  const router = useRouter();
  const { player: playerString } = useLocalSearchParams() as { player: string };
  const [player, setPlayer] = useState<Player>(JSON.parse(playerString));
  const [playerSelection, setPlayerSelection] = useState<
    { name: string; sid: string }[]
  >([]);
  const [updatePlayers, setUpdatePlayers] = useState(false);
  const [playerHasVoted, setPlayerHasVoted] = useState(false);

  useEffect(() => {
    if (playerString) {
      setPlayer(JSON.parse(playerString));
      const newPlayer = JSON.parse(playerString);
      console.log("Player string", newPlayer);
    }
  }, [playerString]);

  useEffect(() => {
    const getAllPlayers = async () => {
      try {
        const response = await axios.get(`${backendUrl}/players`);
        const filteredPlayers = response.data.players
          .filter((item: { is_alive: boolean }) => item.is_alive)
          .filter((item: { sid: string }) => item.sid !== player.sid);
        setPlayerSelection(filteredPlayers);
        setUpdatePlayers(false);
      } catch (error) {
        console.error(error);
      }
    };

    getAllPlayers();
  }, [updatePlayers]);

  const handleVote = (sid: string) => {
    setPlayerHasVoted(true);
    socket.emit("vote_kill", { sid });
    //router.push({
    //  pathname: "/(tabs)/GameInterface",
    //  params: { player: JSON.stringify(player) },
    //});
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => (
    <View className="flex-row justify-between items-center p-2 bg-white my-1 rounded-lg">
      <Text className="text-lg">{item.name}</Text>
      <Button
        title="Vote"
        disabled={playerHasVoted}
        onPress={() => handleVote(item.sid)}
      />
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-gray-900 p-4">
      <Text className="text-white text-center text-2xl mb-4">
        Choose a player to vote for killing:
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

export default DayVote;
