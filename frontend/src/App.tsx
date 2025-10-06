import { useState, useEffect } from "react";
import { OnboardingElite } from "./components/OnboardingElite";
import { ChatInterfaceElite } from "./components/ChatInterfaceElite";
import { FocusModeElite } from "./components/FocusModeElite";
import { useAuthStore } from "./store/authStore";
import type { CoachType } from "./api";

type AppState = "onboarding" | "chat" | "focus";

export default function App() {
  const { isAuthenticated, user, fetchCurrentUser } = useAuthStore();
  const [appState, setAppState] = useState<AppState>("onboarding");
  const [selectedCoach, setSelectedCoach] = useState<CoachType>("coach");
  const [isLoading, setIsLoading] = useState(true);

  // 应用启动时检查登录状态
  useEffect(() => {
    const initApp = async () => {
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

  if (isLoading) {
    return (
      <div className="size-full flex items-center justify-center bg-gradient-to-br from-[#2B69B6] to-[#4DD0E1]">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  console.log("Current appState:", appState, "user:", user);

  return (
    <div className="size-full bg-gradient-to-br from-[#2B69B6] to-[#4DD0E1]">
      {appState === "onboarding" && (
        <OnboardingElite onComplete={handleOnboardingComplete} />
      )}

      {appState === "chat" && (
        <ChatInterfaceElite
          coachType={user?.coach_selection || selectedCoach}
          onStartFocus={handleStartFocus}
        />
      )}

      {appState === "focus" && <FocusModeElite onExit={handleExitFocus} />}
    </div>
  );
}