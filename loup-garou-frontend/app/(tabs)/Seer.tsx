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
  Animated,
} from "react-native";
import axios from "axios";
import { socket } from "../../utils/sockets";
import { Player } from "../../types";
import { backendUrl } from "@/utils/config";

const Seer = ({ seerName }: { visible: boolean; seerName: string }) => {
  const router = useRouter();
  const [players, setPlayers] = useState<{ name: string; sid: string }[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);
  const [playerRole, setPlayerRole] = useState<string | null>(null);
  const [fadeAnim] = useState(new Animated.Value(0));
  const [visible, setVisible] = useState(true);
  const [confirmPressed, setConfirmPressed] = useState(false);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get(`${backendUrl}/players`);
        const allPlayers = response.data.players;
        setPlayers(
          allPlayers.filter((player: Player) => player.name !== seerName),
        );
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    };
    fetchPlayers();
  }, []);

  const handlePlayerSelection = (sid: string) => {
    setSelectedPlayer(sid);
    setPlayerRole(null);
  };

  const handleSeerAction = async () => {
    if (selectedPlayer) {
      socket.emit("seer_check", selectedPlayer);

      socket.once("role_reveal", (data: { role: string }) => {
        setPlayerRole(data.role);
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }).start();
      });
      setConfirmPressed(true);
    }
  };

  const handleOnClose = () => {
    console.log("closing seer modal");
    setVisible(false);
    router.push("/(tabs)/GameInterface");
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => {
    return (
      <TouchableOpacity
        onPress={() => handlePlayerSelection(item.sid)}
        style={{
          padding: 10,
          backgroundColor: selectedPlayer === item.sid ? "lightblue" : "white",
          marginVertical: 5,
          borderRadius: 5,
          borderWidth: 1,
          borderColor: "#ccc",
        }}
        disabled={confirmPressed}
      >
        <Text>{item.name}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      onRequestClose={handleOnClose}
    >
      <SafeAreaView className="flex-1 p-5 bg-gray-100">
        <Text className="text-lg font-bold text-center my-2">
          Choisissez un joueur pour voir son rôle:
        </Text>
        <FlatList
          data={players}
          renderItem={renderPlayer}
          keyExtractor={(item) => item.sid}
        />
        {selectedPlayer && !playerRole && (
          <Button
            title="Voir le rôle du joueur"
            onPress={handleSeerAction}
            disabled={!selectedPlayer}
          />
        )}
        {playerRole && (
          <Animated.View
            style={{ opacity: fadeAnim }}
            className="mt-5 p-5 bg-white rounded shadow"
          >
            <Text className="text-lg font-bold text-center mb-2">
              The player's role is: {playerRole}
            </Text>
            <Button title="Confirm" onPress={handleOnClose} />
          </Animated.View>
        )}
      </SafeAreaView>
    </Modal>
  );
};

export default Seer;
