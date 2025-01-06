import { io } from "socket.io-client";
import { backendUrl } from "@/utils/config";

export const socket = io(backendUrl, {
  autoConnect: true,
  transports: ["websocket"],
});

socket.on("connect", () => {
  console.log("Socket connected");
});

socket.on("connect_error", (error) => {
  console.log("Socket connection error:", error);
});
