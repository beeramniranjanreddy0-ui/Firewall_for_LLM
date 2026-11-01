import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { LogsPage } from "./pages/LogsPage";
import { PromptTestingPage } from "./pages/PromptTestingPage";
import { SecurityEventsPage } from "./pages/SecurityEventsPage";

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/prompt-testing" element={<PromptTestingPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/security-events" element={<SecurityEventsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
