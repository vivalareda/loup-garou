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
  cupid: {
    name: "Cupidon",
    description:
      "La première nuit, choisissez deux joueurs qui tomberont amoureux. Si l'un meurt, l'autre meurt aussi.",
  },
  hunter: {
    name: "Chasseur",
    description:
      "Si vous mourez, vous pouvez immédiatement tuer un autre joueur en utilisant votre dernière balle",
  },
  witch: {
    name: "Sorcière",
    description:
      "Vous avez deux potions : une pour sauver un joueur tué par les loups-garous, une pour éliminer un joueur. Utilisable une seule fois chacune",
  },
  littleGirl: {
    name: "Petite Fille",
    description:
      "Chaque nuit, vous pouvez espionner les loups-garous, mais attention à ne pas vous faire repérer",
  },
};

export function getRoleDescription(roleName: string): string | undefined {
  const role = roles[roleName];
  return role ? role.description : undefined;
}
