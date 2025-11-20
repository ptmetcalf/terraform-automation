"use client";

import { TicketsPanel } from "@/components/tickets-panel";
import { useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useState } from "react";
import { WeatherCard } from "@/components/weather";
import { MoonCard } from "@/components/moon";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");

  // 🪁 Frontend Actions: https://docs.copilotkit.ai/microsoft-agent-framework/frontend-actions
  useCopilotAction({
    name: "setThemeColor",
    parameters: [{
      name: "themeColor",
      description: "The theme color to set. Make sure to pick nice colors.",
      required: true, 
    }],
    handler({ themeColor }) {
      setThemeColor(themeColor);
    },
  });

  //🪁 Generative UI: https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui
  useCopilotAction({
    name: "get_weather",
    description: "Get the weather for a given location.",
    available: "disabled",
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />
    },
  }, [themeColor]);

  // 🪁 Human In the Loop: https://docs.copilotkit.ai/microsoft-agent-framework/human-in-the-loop
  useCopilotAction({
    name: "go_to_moon",
    description: "Go to the moon on request. This action requires human approval and will render the MoonCard UI for confirmation.",
    available: "disabled",
    renderAndWaitForResponse: ({ respond, status}) => {
      return <MoonCard themeColor={themeColor} status={status} respond={respond} />
    },
  }, [themeColor]);

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <CopilotSidebar
        disableSystemMessage={true}
        clickOutsideToClose={false}
        labels={{
          title: "Popup Assistant",
          initial: "👋 Hi, there! You're chatting with an agent."
        }}
        suggestions={[
          {
            title: "Generative UI",
            message: "Get the weather in San Francisco.",
          },
          {
            title: "Frontend Tools",
            message: "Set the theme to green.",
          },
          {
            title: "Human In the Loop",
            message: "Please go to the moon.",
          },
          {
            title: "Ticket Monitor",
            message: "Summarize all open tickets and their current stages.",
          },
          {
            title: "Terraform Plan",
            message: "Run a terraform plan for the homelab workspace.",
          },
          {
            title: "Cost & Security",
            message: "Share the latest cost and security findings for my tickets.",
          }
        ]}
      >
        <YourMainContent themeColor={themeColor} />
      </CopilotSidebar>
    </main>
  );
}

function YourMainContent({ themeColor }: { themeColor: string }) {
  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="min-h-screen flex justify-center items-center p-6 transition-colors duration-300"
    >
      <TicketsPanel />
    </div>
  );
}
