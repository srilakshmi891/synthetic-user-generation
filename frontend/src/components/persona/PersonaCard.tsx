import { Link } from "react-router-dom";
import { MapPin, Briefcase } from "lucide-react";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { PersonaAvatar } from "./PersonaAvatar";
import { truncate, formatDate } from "../../utils/format";
import type { StoredPersona } from "../../types/persona";

interface PersonaCardProps {
  persona: StoredPersona;
}

export function PersonaCard({ persona }: PersonaCardProps) {
  const { basic_info, demographics, occupation, quote } = persona;

  return (
    <Link to={`/personas/${persona.id}`}>
      <Card hover padding="md" className="h-full">
        <div className="flex items-start gap-4">
          <PersonaAvatar name={basic_info.full_name} />
          <div className="min-w-0 flex-1">
            <h3 className="truncate font-semibold text-slate-900">
              {basic_info.full_name}
            </h3>

            <p className="mt-0.5 flex items-center gap-1 text-sm text-slate-500">
              <Briefcase className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{occupation.job_title}</span>
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="brand">{demographics.age} yrs</Badge>
          <Badge>{demographics.gender}</Badge>
          <Badge variant="accent">{occupation.industry}</Badge>
        </div>

        <p className="mt-4 flex items-start gap-1.5 text-xs text-slate-500">
          <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          {demographics.location}
        </p>

        <blockquote className="mt-4 border-l-2 border-brand-200 pl-3 text-sm italic text-slate-600">
          &ldquo;{truncate(quote, 100)}&rdquo;
        </blockquote>

        <p className="mt-4 text-xs text-slate-400">
          {formatDate(persona.createdAt)}
        </p>
      </Card>
    </Link>
  );
}