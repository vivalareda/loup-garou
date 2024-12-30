import React, { useEffect, useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { Text, Button } from "react-native";
import axios from "axios";
import { useRouter } from "expo-router";
import { socket } from "@/utils/sockets.js";
import { Player } from "../../types";
import { useLocalSearchParams } from "expo-router";

const waitingRoom = () => {
  const { player: playerString } = useLocalSearchParams() as { player: string };
  const [player, setPlayer] = useState<Player>(JSON.parse(playerString));
  const [playerHasRole, setPlayerHasRole] = useState(false);

  const router = useRouter();
  const [players, setPlayers] = useState<Player[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const getAllPlayers = async () => {
      try {
        const response = await axios.get("http://192.168.2.215:5001/players");
        const playerData = response.data.players;
        setPlayers(playerData);
      } catch (error) {
        console.error(error);
      }
    };

    getAllPlayers();
  }, []);

  const assignRole = (data: { role: string }) => {
    const newPlayer = { ...player, role: data.role };
    console.log("The new player is: ", newPlayer);
    setPlayer(newPlayer);
    setPlayerHasRole(true);
  };

  useEffect(() => {
    if (isReady) {
      socket.emit("assign_roles");

      socket.once("role_assigned", (data) => {
        assignRole(data);
      });
    }

    return () => {
      socket.off("assign_roles");
    };
  }, [isReady]);

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
      <Button title="Start Game" onPress={() => setIsReady(true)} />
    </SafeAreaView>
  );
};

export default waitingRoom;
