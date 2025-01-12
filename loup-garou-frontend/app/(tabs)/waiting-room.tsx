import React, { useEffect, useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { Text, View, Button } from "react-native";
import axios from "axios";
import { useRouter } from "expo-router";
import { socket } from "@/utils/sockets.js";
import { Player } from "../../types";
import { useLocalSearchParams } from "expo-router";
import { backendUrl } from "@/utils/config";
import { MotiView } from "moti";
import Svg, { Circle } from "react-native-svg";

type CustomCircleProps = {
  radius?: number;
  strokeWidth?: number;
  color?: string;
  delay?: number;
};

function CustomCircle({
  radius = 40,
  strokeWidth = 4,
  color = "#000",
  delay = 5,
}: CustomCircleProps) {
  const circumference = 2 * Math.PI * radius;
  const halfCircle = radius + strokeWidth;
  const wantedAngle = 60;
  const angleInRadians = (wantedAngle * Math.PI) / 180;
  const arcLength = radius * angleInRadians;
  const strokeDashoffset = circumference - arcLength;
  const initialAngle = (180 - wantedAngle) / 2 + wantedAngle;

  return (
    <MotiView
      style={{ width: radius * 2, height: radius * 2, position: "absolute" }}
      from={{ rotate: `-${initialAngle}deg` }}
      animate={{ rotate: `-${360 + initialAngle}deg` }}
      transition={{
        damping: 80,
        mass: 1,
        stiffness: 200,
        loop: true,
        delay,
      }}
    >
      <Svg
        width={halfCircle * 2}
        height={halfCircle * 2}
        viewBox={`0 0 ${halfCircle * 2} ${halfCircle * 2}`}
      >
        <Circle
          cx="50%"
          cy="50%"
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDashoffset={strokeDashoffset}
          strokeDasharray={circumference}
        />
      </Svg>
    </MotiView>
  );
}

function LoadingCircles({
  size = 30,
  count = 3,
  frontColor = "#504774",
  backColor = "#EF7519",
  stagger = 100,
}) {
  return (
    <View>
      <View className="items-center justify-center">
        {[...Array(count).keys()].map((i) => {
          const strokeWidth = Math.floor(size / 3);
          const radius = i * strokeWidth * 2 + size;
          return (
            <CustomCircle
              key={`back-${i}`}
              radius={radius}
              delay={stagger + i * stagger}
              color={backColor}
              strokeWidth={strokeWidth}
            />
          );
        })}
      </View>
      <View className="items-center justify-center">
        {[...Array(count).keys()].map((i) => {
          const strokeWidth = Math.floor(size / 3);
          const radius = i * strokeWidth * 2 + size;
          return (
            <CustomCircle
              key={`front-${i}`}
              radius={radius}
              delay={i * stagger}
              color={frontColor}
              strokeWidth={strokeWidth}
            />
          );
        })}
      </View>
    </View>
  );
}

const WaitingRoom = () => {
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
    <SafeAreaView className="flex-1 items-center justify-center">
      <View className="space-y-5 gap-36 pt-32">
        <LoadingCircles size={30} count={3} stagger={100} />
        <Text className="text-white">
          {players.length === 0
            ? "Vous etes seul dans la salle d'attente, attendez que d'autres joueurs vous rejoignent"
            : `${players.map((player) => player.name).join(", ")} attendent avec vous`}
        </Text>
      </View>
    </SafeAreaView>
  );
};

export default WaitingRoom;
