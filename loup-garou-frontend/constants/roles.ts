export interface Role {
  name: string;
  description: string;
}

export const roles: { [key: string]: Role } = {
  werewolf: {
    name: "Loup-Garou",
    description:
      "Chaque nuit, votez avec les autres loups-garous pour dévorer un villageois",
  },
  villager: {
    name: "Villageois",
    description:
      "Votez pendant la journée pour éliminer les loups-garous suspects",
  },
  seer: {
    name: "Voyante",
    description:
      "Chaque nuit, inspectez un joueur pour découvrir s'il est un loup-garou",
  },
  cupidon: {
    name: "Cupidon",
    description:
      "La première nuit, choisissez deux joueurs qui tomberont amoureux. Si l'un meurt, l'autre meurt aussi.",
  },
};

export function getRoleDescription(roleName: string): string | undefined {
  const role = roles[roleName];
  return role ? role.description : undefined;
}
