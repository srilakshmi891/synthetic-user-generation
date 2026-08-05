import { Routes, Route } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { ResearchWorkspace } from "./pages/ResearchWorkspace";
import { PersonaGallery } from "./pages/PersonaGallery";
import { PersonaDetails } from "./pages/PersonaDetails";

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/workspace" element={<ResearchWorkspace />} />

            <Route path="/personas" element={<PersonaGallery />} />

            <Route
                path="/personas/:id"
                element={<PersonaDetails />}
            />
        </Routes>
    );
}