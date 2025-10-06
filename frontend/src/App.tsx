import { useState } from "react";
import { OnboardingElite } from "./components/OnboardingElite";
import { ChatInterfaceElite } from "./components/ChatInterfaceElite";
import { FocusModeElite } from "./components/FocusModeElite";

type CoachType = "wise" | "companion" | "expert";
type AppState = "onboarding" | "chat" | "focus";

export default function App() {
  const [appState, setAppState] =
    useState<AppState>("onboarding");
  const [selectedCoach, setSelectedCoach] =
    useState<CoachType>("wise");

  const handleOnboardingComplete = (coachType: CoachType) => {
    setSelectedCoach(coachType);
    setAppState("chat");
  };

  const handleStartFocus = () => {
    setAppState("focus");
  };

  const handleExitFocus = () => {
    setAppState("chat");
  };

  return (
    <div className="size-full">
      {appState === "onboarding" && (
        <OnboardingElite
          onComplete={handleOnboardingComplete}
        />
      )}

      {appState === "chat" && (
        <ChatInterfaceElite
          coachType={selectedCoach}
          onStartFocus={handleStartFocus}
        />
      )}

      {appState === "focus" && (
        <FocusModeElite onExit={handleExitFocus} />
      )}
    </div>
  );
}