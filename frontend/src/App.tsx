import { useState, useEffect } from "react";
import { OnboardingElite } from "./components/OnboardingElite";
import { ChatInterfaceElite } from "./components/ChatInterfaceElite";
import { FocusModeElite } from "./components/FocusModeElite";
import { HealthDataEntry } from "./components/HealthDataEntry";
import DigitalTwinDashboard from "./components/energy/DigitalTwinDashboard";
import HealthSyncTest from "./pages/HealthSyncTest";
import { DeviceFrame } from "./components/DeviceFrame";
import { DevicePreviewToggle } from "./components/DevicePreviewToggle";
import { useAuthStore } from "./store/authStore";
import { initCapacitor, isNativePlatform } from "./utils/capacitor";
import type { CoachType } from "./api";

type AppState = "onboarding" | "chat" | "focus" | "health" | "energy" | "healthSync";

export default function App() {
  const { isAuthenticated, user, fetchCurrentUser } = useAuthStore();
  // 临时设置为healthSync用于测试
  const [appState, setAppState] = useState<AppState>("healthSync");
  const [selectedCoach, setSelectedCoach] = useState<CoachType>("companion");
  const [isLoading, setIsLoading] = useState(false);

  // 应用启动时初始化
  useEffect(() => {
    const initApp = async () => {
      // 初始化 Capacitor 原生功能
      await initCapacitor();

      console.log("App init - isAuthenticated:", isAuthenticated);
      if (isAuthenticated) {
        try {
          await fetchCurrentUser();
          console.log("Fetched current user, going to chat");
          setAppState("chat");
        } catch (error) {
          console.error("Failed to fetch user:", error);
          setAppState("onboarding");
        }
      }
      setIsLoading(false);
    };
    initApp();
  }, [isAuthenticated, fetchCurrentUser]);

  const handleOnboardingComplete = (coachType: CoachType) => {
    console.log("Onboarding complete with coach:", coachType);
    setSelectedCoach(coachType);
    setAppState("chat");
  };

  const handleStartFocus = () => {
    setAppState("focus");
  };

  const handleExitFocus = () => {
    setAppState("chat");
  };

  const handleOpenHealth = () => {
    setAppState("health");
  };

  const handleExitHealth = () => {
    setAppState("chat");
  };

  const handleOpenEnergy = () => {
    setAppState("energy");
  };

  const handleExitEnergy = () => {
    setAppState("chat");
  };

  const handleOpenHealthSync = () => {
    setAppState("healthSync");
  };

  const handleExitHealthSync = () => {
    setAppState("chat");
  };

  if (isLoading) {
    return (
      <div className="size-full flex items-center justify-center bg-gradient-to-br from-[#2B69B6] to-[#4DD0E1]">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  console.log("Current appState:", appState, "user:", user);

  return (
    <DeviceFrame>
      <div className="w-full min-h-full bg-gradient-to-br from-[#2B69B6] to-[#4DD0E1]">
        {appState === "onboarding" && (
          <OnboardingElite onComplete={handleOnboardingComplete} />
        )}

        {appState === "chat" && (
          <ChatInterfaceElite
            coachType={user?.coach_selection || selectedCoach}
            onStartFocus={handleStartFocus}
            onOpenHealth={handleOpenHealth}
            onOpenEnergy={handleOpenEnergy}
          />
        )}

        {appState === "focus" && <FocusModeElite onExit={handleExitFocus} />}

        {appState === "health" && <HealthDataEntry onBack={handleExitHealth} />}

        {appState === "energy" && <DigitalTwinDashboard onBack={handleExitEnergy} />}

        {appState === "healthSync" && <HealthSyncTest />}
      </div>

      {/* 设备预览切换器 - 仅在开发环境且非原生平台显示 */}
      {import.meta.env.DEV && !isNativePlatform && <DevicePreviewToggle />}
    </DeviceFrame>
  );
}