import { useParams, Link } from "react-router-dom";
import { MessageSquare, ArrowLeft } from "lucide-react";
import { usePersonas } from "../context/PersonaContext";
import { Button } from "../components/ui/Button";

export function PersonaDetails() {
    const { id } = useParams();
    const { personas } = usePersonas();

    const persona = personas.find((p) => p.id === id);

    if (!persona) {
        return <h2>Persona not found</h2>;
    }

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Link to="/personas">
                        <Button variant="ghost" size="sm">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <h1 className="text-3xl font-bold">
                        {persona.basic_info.full_name}
                    </h1>
                </div>
                <Link to={`/interview?personaId=${persona.id}`}>
                    <Button icon={<MessageSquare className="h-4 w-4" />}>
                        Interview Persona
                    </Button>
                </Link>
            </div>


            <section>
                <h2 className="text-xl font-semibold">Basic Information</h2>
                <p><b>Bio:</b> {persona.basic_info.bio}</p>
                <p><b>Avatar:</b> {persona.basic_info.avatar_description}</p>
            </section>

            <section>
                <h2 className="text-xl font-semibold">Demographics</h2>
                <p>Age: {persona.demographics.age}</p>
                <p>Gender: {persona.demographics.gender}</p>
                <p>Location: {persona.demographics.location}</p>
                <p>Marital Status: {persona.demographics.marital_status}</p>
                <p>Income: {persona.demographics.household_income}</p>
            </section>

            <section>
                <h2 className="text-xl font-semibold">Education</h2>
                <p>Degree: {persona.education.degree_level}</p>
                <p>Field: {persona.education.field_of_study}</p>
                <p>Institution: {persona.education.institution_type}</p>
            </section>

            <section>
                <h2 className="text-xl font-semibold">Occupation</h2>
                <p>Job: {persona.occupation.job_title}</p>
                <p>Industry: {persona.occupation.industry}</p>
                <p>Company Size: {persona.occupation.company_size}</p>
                <p>Work Mode: {persona.occupation.work_mode}</p>

                <ul>
                    {persona.occupation.key_responsibilities.map((r, i) => (
                        <li key={i}>• {r}</li>
                    ))}
                </ul>
            </section>

            <section>
                <h2 className="text-xl font-semibold">Goals</h2>

                <h3>Primary Goals</h3>
                <ul>
                    {persona.goals.primary_goals.map((g, i) => (
                        <li key={i}>• {g}</li>
                    ))}
                </ul>

                <h3>Secondary Goals</h3>
                <ul>
                    {persona.goals.secondary_goals.map((g, i) => (
                        <li key={i}>• {g}</li>
                    ))}
                </ul>

                <h3>Personal Aspirations</h3>
                <ul>
                    {persona.goals.personal_aspirations.map((g, i) => (
                        <li key={i}>• {g}</li>
                    ))}
                </ul>
            </section>

            <section>
                <h2 className="text-xl font-semibold">Quote</h2>
                <blockquote>{persona.quote}</blockquote>
            </section>

        </div>
    );
}