import { createRoot } from "react-dom/client";
import VerifixiaApp from "./VerifixiaApp.tsx";
import "./global_base_styles.css";
import { ThemeProvider } from "./components/theme-provider";

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <VerifixiaApp />
  </ThemeProvider>
);
