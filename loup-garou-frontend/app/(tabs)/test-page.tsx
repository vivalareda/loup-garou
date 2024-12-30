import React, { useEffect, useState } from "react";
import { View, Text, TextInput, Button } from "react-native";
import { socket } from "@/utils/sockets";
import axios from "axios";

const TestSocketPage = () => {
  const [message, setMessage] = useState("");
  const [receivedMessage, setReceivedMessage] = useState("");

  useEffect(() => {
    socket.on("test_event", (data) => {
      console.log(data.message);
      setReceivedMessage(data.message);
    });

    return () => {
      socket.off("test_event");
    };
  }, []);

  const sendMessage = () => {
    socket.emit("test_event", { message });
  };

  const triggerServerEvent = async () => {
    try {
      const response = await axios.get(
        "http://192.168.2.215:5001/trigger_test_event",
      );
      console.log(response.data.status);
    } catch (error) {
      console.error("Error triggering event:", error);
    }
  };

  return (
    <View className="flex-1 p-4 justify-center">
      <Text className="text-2xl mb-4 text-center">Socket.IO Test Page</Text>
      <TextInput
        className="h-10 border border-gray-400 mb-4 px-2"
        value={message}
        onChangeText={setMessage}
        placeholder="Enter message"
      />
      <Button title="Send Message" onPress={sendMessage} />
      <Button title="Trigger Server Event" onPress={triggerServerEvent} />
      <Text className="mt-4 text-lg text-center">
        Received Message: {receivedMessage}
      </Text>
    </View>
  );
};

export default TestSocketPage;
