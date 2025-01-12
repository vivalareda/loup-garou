import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Button,
} from "react-native";
import { socket } from "@/utils/sockets";
import { Picker } from "@react-native-picker/picker";
import axios from "axios";
import { backendUrl } from "@/utils/config";

interface Player {
  name: string;
  sid: string;
  role?: string;
  is_alive: boolean;
}

interface MockPlayer extends Player {
  isMock: boolean;
}

interface PendingAction {
  type: string;
  data?: any;
  options?: any;
}

const MockGameManager = () => {
  const [mockPlayers, setMockPlayers] = useState<MockPlayer[]>([]);
  const [numOfMockPlayers, setNumOfMockPlayers] = useState<number>(0);
  const [pendingActions, setPendingActions] = useState<{
    [key: string]: PendingAction;
  }>({});
  const [werewolfVotes, setWerewolfVotes] = useState<{ [key: string]: string }>(
    {},
  );

  // Fetch players
  const fetchPlayers = async () => {
    try {
      const response = await axios.get(`${backendUrl}/players`);
      const allPlayers = response.data.players;
      setMockPlayers(allPlayers);
    } catch (error) {
      console.error("Error fetching players:", error);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  useEffect(() => {
    // Role assignment
    socket.on("role_assigned", (data: { role: string; sid: string }) => {
      setMockPlayers((prev) =>
        prev.map((p) => (p.sid === data.sid ? { ...p, role: data.role } : p)),
      );
    });

    // Cupidon choice
    socket.on("cupidon_choice", (data: { message: string }) => {
      const cupid = mockPlayers.find((p) => p.role === "cupid");
      if (cupid) {
        setPendingActions((prev) => ({
          ...prev,
          [cupid.sid]: { type: "cupidon", data },
        }));
      }
    });

    // Werewolf phase
    socket.on(
      "werewolf_wake_up",
      (data: { message: string; other_werewolves: string[] }) => {
        const werewolves = mockPlayers.filter((p) => p.role === "werewolf");
        werewolves.forEach((werewolf) => {
          setPendingActions((prev) => ({
            ...prev,
            [werewolf.sid]: { type: "werewolf", data },
          }));
        });
      },
    );

    console.log(
      "Socket listeners count:",
      socket.listeners("alert_lovers").length,
    );
    socket.on("lover_can_close", handleIsInLove);

    // New werewolf vote count
    socket.on(
      "new_selection_count",
      (data: { werewolf: string; name: string; vote: string }) => {
        setWerewolfVotes((prev) => ({
          ...prev,
          [data.werewolf]: data.vote,
        }));
      },
    );

    // Witch actions
    socket.on("witch_heal", (data: { message: string; victim: string }) => {
      const witch = mockPlayers.find((p) => p.role === "witch");
      if (witch) {
        setPendingActions((prev) => ({
          ...prev,
          [witch.sid]: { type: "witch_heal", data },
        }));
      }
    });

    socket.on("witch_kill", (data: { message: string }) => {
      const witch = mockPlayers.find((p) => p.role === "witch");
      if (witch) {
        setPendingActions((prev) => ({
          ...prev,
          [witch.sid]: { type: "witch_kill", data },
        }));
      }
    });

    // Day vote
    socket.on("day_vote", () => {
      const alivePlayers = mockPlayers.filter((p) => p.is_alive);
      console.log("Alive players:", alivePlayers);
      alivePlayers.forEach((player) => {
        setPendingActions((prev) => ({
          ...prev,
          [player.sid]: { type: "day_vote" },
        }));
      });
    });

    // Player death
    socket.on("alert_dead", () => {
      const playerSid = socket.id;
      setMockPlayers((prev) =>
        prev.map((p) => (p.sid === playerSid ? { ...p, is_alive: false } : p)),
      );
    });

    return () => {
      socket.off("role_assigned");
      socket.off("cupidon_choice");
      socket.off("werewolf_wake_up");
      socket.off("new_selection_count");
      socket.off("witch_heal");
      socket.off("witch_kill");
      socket.off("day_vote");
      socket.off("alert_dead");
      socket.off("lover_can_close", handleIsInLove);
    };
  }, [mockPlayers]);

  useEffect(() => {
    fetchPlayers();
  }, [pendingActions]);

  const handleIsInLove = (data: { lover: string }) => {
    console.log("Lover alert received", data);
    socket.emit("lover_alert_closed");
  };

  const emitAlertLoversClosed = () => {
    socket.emit("alert_lovers_closed");
    socket.emit("alert_lovers_closed");
  };

  // Initialize mock players
  const addMockPlayers = (count: number) => {
    const newPlayers: MockPlayer[] = [];

    for (let i = 0; i < count; i++) {
      const mockPlayer: MockPlayer = {
        name: `TestPlayer${mockPlayers.length + i + 1}`,
        sid: `mock_${Date.now()}_${i}`,
        is_alive: true,
        isMock: true,
      };
      newPlayers.push(mockPlayer);
    }

    socket.emit("add_mock_players", {
      players: newPlayers,
      controllerSid: socket.id,
    });

    setMockPlayers((prev) => [...prev, ...newPlayers]);
  };

  const handleAction = (playerId: string, actionType: string, data: any) => {
    switch (actionType) {
      case "cupidon":
        socket.emit("cupidon_selection_complete", data);
        break;
      case "werewolf":
        socket.emit("werewolf_kill", data);
        break;
      case "witch_heal":
        socket.emit("witch_heal_victim");
        break;
      case "witch_kill":
        socket.emit("witch_kill_victim", { sid: data });
        break;
      case "day_vote":
        socket.emit("vote_kill", { sid: data });
        break;
    }

    setPendingActions((prev) => {
      const newActions = { ...prev };
      delete newActions[playerId];
      return newActions;
    });
  };

  const renderActionControls = (player: MockPlayer, action: PendingAction) => {
    switch (action.type) {
      case "day_vote":
        return (
          <View className="mt-2">
            {mockPlayers
              .filter((p) => p.is_alive && p.sid !== player.sid)
              .map((target) => (
                <TouchableOpacity
                  key={target.sid}
                  onPress={() =>
                    handleAction(player.sid, "day_vote", target.sid)
                  }
                  className="bg-blue-500 p-2 rounded mt-1"
                >
                  <Text className="text-white">Vote {target.name}</Text>
                </TouchableOpacity>
              ))}
          </View>
        );

      case "werewolf":
        return (
          <View className="mt-2">
            {mockPlayers
              .filter((p) => p.is_alive && p.role !== "werewolf")
              .map((target) => (
                <TouchableOpacity
                  key={target.sid}
                  onPress={() =>
                    handleAction(player.sid, "werewolf", target.sid)
                  }
                  className="bg-blue-500 p-2 rounded mt-1"
                >
                  <Text className="text-white">Kill {target.name}</Text>
                </TouchableOpacity>
              ))}
          </View>
        );

      // Add more action type renders as needed

      default:
        return null;
    }
  };

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <View className="mb-6">
          <Text className="text-xl font-bold mb-4">Mock Game Controls</Text>
          <TextInput
            value={numOfMockPlayers.toString()}
            className="border p-2 rounded w-20 mb-6"
            onChangeText={(text) => setNumOfMockPlayers(parseInt(text))}
          />
          <Picker
            className="border p-2 rounded w-20 mb-6"
            onValueChange={(value) => setNumOfMockPlayers(parseInt(value))}
            selectedValue={numOfMockPlayers.toString()}
          >
            <Picker.Item label="1" value="1" />
            <Picker.Item label="2" value="2" />
            <Picker.Item label="3" value="3" />
            <Picker.Item label="4" value="4" />
            <Picker.Item label="5" value="5" />
            <Picker.Item label="6" value="6" />
            <Picker.Item label="7" value="7" />
            <Picker.Item label="8" value="8" />
            <Picker.Item label="9" value="9" />
            <Picker.Item label="10" value="10" />
          </Picker>

          <TouchableOpacity
            onPress={() => addMockPlayers(numOfMockPlayers)}
            className="bg-blue-500 p-4 rounded"
          >
            <Text className="text-white text-center">Add Mock Players</Text>
          </TouchableOpacity>
        </View>

        <View className="mb-6">
          <Text className="font-bold mb-2">
            Mock Players ({mockPlayers.length})
          </Text>
          {mockPlayers.map((player) => (
            <View key={player.sid} className="bg-white p-4 rounded mb-2">
              <Text style={{ color: !player.is_alive ? "red" : "black" }}>
                {player.name} - {player.role || "No role"}
                {!player.is_alive && " (Dead)"}
              </Text>

              {pendingActions[player.sid] && (
                <View className="mt-2 bg-yellow-100 p-2 rounded">
                  <Text>
                    Action Required: {pendingActions[player.sid].type}
                  </Text>
                  {renderActionControls(player, pendingActions[player.sid])}
                </View>
              )}
            </View>
          ))}
        </View>

        <Button
          title="Emit alert lovers closed"
          onPress={emitAlertLoversClosed}
        />
      </View>
    </ScrollView>
  );
};

export default MockGameManager;
