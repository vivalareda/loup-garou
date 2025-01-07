import React from "react";
import { SafeAreaView, Text, TouchableOpacity, View } from "react-native";
import { useRouter } from "expo-router";

const DeathScreen: React.FC = () => {
  return (
    <SafeAreaView className="flex-1 bg-gray-900 items-center justify-center">
      <View className="w-80 h-80 bg-gradient-to-br from-red-600 to-red-900 rounded-xl items-center justify-center p-6 shadow-xl border border-gray-200">
        <Text className="text-white text-3xl font-bold mb-4 text-center">
          Vous etes mort, pas le droit de parler !
        </Text>
      </View>
    </SafeAreaView>
  );
};

export default DeathScreen;
