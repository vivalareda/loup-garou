import { io } from "socket.io-client";

export const socket = io("http://192.168.2.215:5001", {
  autoConnect: true,
  transports: ["websocket"],
});
