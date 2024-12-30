export interface Role {
  name: string;
  description: string;
}

export const roles: { [key: string]: Role } = {
  werewolf: {
    name: "Werewolf",
    description: "Each night, vote with other werewolves to eat a villager",
  },
  villager: {
    name: "Villager",
    description: "Vote during the day to eliminate suspected werewolves",
  },
  seer: {
    name: "Seer",
    description:
      "Each night, check one player to reveal if they are a werewolf",
  },
  cupidon: {
    name: "Cupidon",
    description:
      "On the first night, choose two players to fall in love. If one dies, the other dies too.",
  },
};

export function getRoleDescription(roleName: string): string | undefined {
  const role = roles[roleName];
  return role ? role.description : undefined;
}
