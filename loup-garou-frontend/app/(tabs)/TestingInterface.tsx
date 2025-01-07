import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { socket } from "@/utils/sockets";

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
  const [pendingActions, setPendingActions] = useState<{
    [key: string]: PendingAction;
  }>({});
  const [werewolfVotes, setWerewolfVotes] = useState<{ [key: string]: string }>(
    {},
  );

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

  useEffect(() => {
    // Role assignment
    socket.on("role_assigned", (data: { role: string }) => {
      const player = mockPlayers.find((p) => p.sid === socket.id);
      if (player) {
        setMockPlayers((prev) =>
          prev.map((p) =>
            p.sid === socket.id ? { ...p, role: data.role } : p,
          ),
        );
      }
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
    };
  }, [mockPlayers]);

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
          <TouchableOpacity
            onPress={() => addMockPlayers(4)}
            className="bg-blue-500 p-4 rounded"
          >
            <Text className="text-white text-center">Add 4 Mock Players</Text>
          </TouchableOpacity>
        </View>

        <View className="mb-6">
          <Text className="font-bold mb-2">
            Mock Players ({mockPlayers.length})
          </Text>
          {mockPlayers.map((player) => (
            <View key={player.sid} className="bg-white p-4 rounded mb-2">
              <Text>
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
      </View>
    </ScrollView>
  );
};

export default MockGameManager;
