import { io } from "socket.io-client";
import { backendUrl } from "@/utils/config";

export const socket = io(backendUrl, {
  autoConnect: true,
  transports: ["websocket"],
});
