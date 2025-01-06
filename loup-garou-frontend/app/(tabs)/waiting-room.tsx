import React, { useEffect, useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { Text, Button } from "react-native";
import axios from "axios";
import { useRouter } from "expo-router";
import { socket } from "@/utils/sockets.js";
import { Player } from "../../types";
import { useLocalSearchParams } from "expo-router";
import { backendUrl } from "@/utils/config";

const waitingRoom = () => {
  const { player: playerString } = useLocalSearchParams() as { player: string };
  const [player, setPlayer] = useState<Player>(JSON.parse(playerString));
  const [playerHasRole, setPlayerHasRole] = useState(false);

  const router = useRouter();
  const [players, setPlayers] = useState<Player[]>([]);
  const [startGame, setStartGame] = useState(false);
  const [updatePlayers, setUpdatePlayers] = useState(false);

  useEffect(() => {
    const getAllPlayers = async () => {
      try {
        const response = await axios.get(`${backendUrl}/players`);
        const playerData = response.data.players;
        setPlayers(playerData);
        setUpdatePlayers(false);
      } catch (error) {
        console.error(error);
      }
    };

    getAllPlayers();
  }, [updatePlayers]);

  useEffect(() => {
    socket.on("update_players_list", () => {
      console.log("Updating players list");
      setUpdatePlayers(true);
    });
  }, []);

  const assignRole = (data: { role: string }) => {
    const newPlayer = { ...player, role: data.role };
    setPlayer(newPlayer);
    setPlayerHasRole(true);
  };

  useEffect(() => {
    socket.on("role_assigned", (data) => {
      assignRole(data);
    });

    return () => {
      socket.off("assign_roles");
    };
  }, []);

  useEffect(() => {
    if (playerHasRole) {
      router.push({
        pathname: "/(tabs)/GameInterface",
        params: { player: JSON.stringify(player) },
      });
    }
  }, [playerHasRole]);

  return (
    <SafeAreaView>
      <Text className="text-white justify-center text-center">
        be patient dawg
      </Text>
      {players.length === 0 ? (
        <Text className="text-white justify-center text-center">
          You are the first player, waiting for others to join
        </Text>
      ) : (
        <Text className="text-white justify-center text-center">
          {players.map((player) => player.name).join(", ")} are waiting with you
        </Text>
      )}
    </SafeAreaView>
  );
};

export default waitingRoom;
