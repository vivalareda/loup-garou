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

const Cupidon = ({
  visible,
  onClose,
}: {
  visible: boolean;
  onClose: () => void;
}) => {
  const router = useRouter();

  const [players, setPlayers] = useState<{ name: string; sid: string }[]>([]);
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([]);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get("http://192.168.2.215:5001/players");
        setPlayers(response.data.players);
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    };

    fetchPlayers();
  }, []);

  const togglePlayerSelection = (sid: string) => {
    setSelectedPlayers((prevSelected) => {
      if (prevSelected.includes(sid)) {
        return prevSelected.filter((id) => id !== sid);
      } else if (prevSelected.length < 2) {
        return [...prevSelected, sid];
      } else {
        return prevSelected;
      }
    });
  };

  const handleCupidonSelection = (selectedPlayers: string[]) => {
    const chosenPlayers = players.filter((player) =>
      selectedPlayers.includes(player.sid),
    );
    socket.emit("cupidon_selection", chosenPlayers);
    onClose();
    router.push("/(tabs)/GameInterface");
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => (
    <TouchableOpacity
      onPress={() => togglePlayerSelection(item.sid)}
      style={{
        padding: 10,
        backgroundColor: selectedPlayers.includes(item.sid)
          ? "lightblue"
          : "white",
        marginVertical: 5,
      }}
    >
      <Text>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <SafeAreaView>
        <Text className="text-white justify-center text-center">
          Choose two players:
        </Text>
        <FlatList
          data={players}
          renderItem={renderPlayer}
          keyExtractor={(item) => item.sid}
        />
        <Button
          title="Confirm Selection"
          onPress={() => handleCupidonSelection(selectedPlayers)}
          disabled={selectedPlayers.length !== 2}
        />
      </SafeAreaView>
    </Modal>
  );
};

export default Cupidon;
