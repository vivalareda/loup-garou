import React, { useEffect, useState } from "react";
import { useRouter } from "expo-router";
import {
  SafeAreaView,
  Text,
  Button,
  FlatList,
  TouchableOpacity,
  Modal,
  View,
} from "react-native";
import axios from "axios";
import { socket } from "../../utils/sockets";
import { Player } from "../../types";
import { backendUrl } from "@/utils/config";

const Hunter = ({
  visible,
  onClose,
  hunterName,
}: {
  visible: boolean;
  onClose: () => void;
  hunterName: string;
}) => {
  const router = useRouter();
  const [players, setPlayers] = useState<{ name: string; sid: string }[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get(`${backendUrl}/players`);
        const allPlayers = response.data.players;
        setPlayers(
          allPlayers.filter((player: Player) => player.name !== hunterName),
        );
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    };
    fetchPlayers();
  }, []);

  const togglePlayerSelection = (sid: string) => {
    setSelectedPlayer(selectedPlayer === sid ? null : sid);
  };

  const handleHunterSelection = (selectedPlayer: string) => {
    const chosenPlayer = players.find(
      (player) => player.sid === selectedPlayer,
    );
    socket.emit("hunter_selection", chosenPlayer);
    onClose();
    router.push("/(tabs)/GameInterface");
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => {
    return (
      <TouchableOpacity
        onPress={() => togglePlayerSelection(item.sid)}
        style={{
          padding: 10,
          backgroundColor: selectedPlayer === item.sid ? "lightblue" : "white",
          marginVertical: 5,
        }}
      >
        <Text>{item.name}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <SafeAreaView>
        <Text className="text-white justify-center text-center">
          Choose a player to take down with you:
        </Text>
        <FlatList
          data={players}
          renderItem={renderPlayer}
          keyExtractor={(item) => item.sid}
        />
        <Button
          title="Confirm Selection"
          onPress={() =>
            selectedPlayer && handleHunterSelection(selectedPlayer)
          }
          disabled={!selectedPlayer}
        />
      </SafeAreaView>
    </Modal>
  );
};

export default Hunter;
