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

const Werewolf = () => {
  const router = useRouter();
  const { player: playerString } = useLocalSearchParams() as { player: string };
  const [player, setPlayer] = useState<Player>(JSON.parse(playerString));
  const [playerSelection, setPlayerSelection] = useState<
    { name: string; sid: string }[]
  >([]);
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);
  const [otherWerewolvesVote, setOtherWerewolvesVote] = useState<{
    [key: string]: string;
  }>({});
  const [totalWerewolves, setTotalWerewolves] = useState<number>(0);

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
        const werewolfCount = playerData.filter(
          (p: Player) => p.role === "werewolf",
        ).length;
        const werewolveSelection = playerData.filter(
          (p: Player) => p.role !== "werewolf",
        );
        setTotalWerewolves(werewolfCount);
        setPlayerSelection(werewolveSelection);
      } catch (error) {
        console.error(error);
      }
    };

    if (player) {
      getAllPlayers();
    }

    socket.on(
      "new_selection_count",
      (data: { werewolf: string; name: string; vote: string }) => {
        setOtherWerewolvesVote((prev) => {
          const newVotes = {
            ...prev,
            [data.werewolf]: data.vote,
          };

          return newVotes;
        });
      },
    );

    return () => {
      socket.off("new_selection_count");
    };
  }, [player, totalWerewolves]);

  useEffect(() => {
    const allVotesEqual = () => {
      const votes = Object.values(otherWerewolvesVote);
      if (votes.length === 0 || votes.length < totalWerewolves) return false;
      if (votes.every((vote) => vote === votes[0])) {
        socket.emit("werewolf_kill", votes[0]);
        console.log("All werewolves agree on killing", votes[0]);
        router.push({
          pathname: "/(tabs)/GameInterface",
          params: { player: JSON.stringify(player) },
        });
      }
    };

    allVotesEqual();
  }, [otherWerewolvesVote, playerSelection]);

  const togglePlayerSelection = (sid: string, name: string) => {
    setSelectedPlayer(sid);
    socket.emit("update_werewolf_selection_count", {
      werewolf: player.name,
      name: name,
      vote: sid,
    });
  };

  const handleWerewolfSelection = () => {
    const chosenPlayer = playerSelection.find((p) => p.sid === selectedPlayer);
    socket.emit("werewolf_kill", chosenPlayer);
    router.push({
      pathname: "/(tabs)/GameInterface",
      params: { player: JSON.stringify(player) },
    });
  };

  const getVoteCount = (sid: string): number => {
    return Object.values(otherWerewolvesVote).filter((vote) => vote === sid)
      .length;
  };

  const allWerewolvesAgree = () => {
    const votes = Object.values(otherWerewolvesVote);
    return votes.length > 0 && votes.every((vote) => vote === selectedPlayer);
  };

  const renderPlayer = ({ item }: { item: { name: string; sid: string } }) => {
    const voteCount = getVoteCount(item.sid);

    return (
      <TouchableOpacity
        onPress={() => togglePlayerSelection(item.sid, item.name)}
        style={{
          padding: 10,
          backgroundColor: selectedPlayer === item.sid ? "lightblue" : "white",
          marginVertical: 5,
          borderRadius: 8,
        }}
      >
        <View
          style={{
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Text style={{ fontSize: 16 }}>{item.name}</Text>
          <View
            style={{
              backgroundColor: "#e0e0e0",
              borderRadius: 12,
              padding: 4,
              minWidth: 24,
              alignItems: "center",
            }}
          >
            <Text style={{ fontSize: 14 }}>
              {voteCount}/{totalWerewolves}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-900 h-full w-full">
      <Text className="text-white justify-center text-center text-xl mb-4">
        Choisissez un joueur à tuer:
      </Text>
      {playerSelection && (
        <FlatList
          data={playerSelection}
          renderItem={renderPlayer}
          keyExtractor={(item) => item.sid}
          className="text-white"
        />
      )}
      <Button
        title="Confirm Selection"
        onPress={handleWerewolfSelection}
        disabled={!allWerewolvesAgree()}
      />
    </SafeAreaView>
  );
};

export default Werewolf;
