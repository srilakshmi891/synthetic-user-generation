import { usePersonas } from "../context/PersonaContext";
import { PersonaCard } from "../components/persona/PersonaCard";

export function PersonaGallery() {
    const { personas } = usePersonas();

    return (
        <div className="p-6">
            <h1 className="mb-6 text-3xl font-bold">
                Persona Gallery
            </h1>

            {personas.length === 0 ? (
                <p>No personas found.</p>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {personas.map((persona) => (
                        <PersonaCard
                            key={persona.id}
                            persona={persona}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}