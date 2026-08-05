import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { StoredPersona } from '../types/persona';
import { loadPersonas, savePersonas } from '../services/storage';

interface PersonaContextValue {
  personas: StoredPersona[];
  addPersonas: (incoming: StoredPersona[]) => void;
  refresh: () => void;
  isLoading: boolean;
}

const PersonaContext = createContext<PersonaContextValue | null>(null);

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [personas, setPersonas] = useState<StoredPersona[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(() => {
    setPersonas(loadPersonas());
  }, []);

  useEffect(() => {
    refresh();
    setIsLoading(false);
  }, [refresh]);

  const addPersonas = useCallback(
    (incoming: StoredPersona[]) => {
      setPersonas((prev) => {
        const merged = [...incoming, ...prev];
        savePersonas(merged);
        return merged;
      });
    },
    []
  );

  const value = useMemo(
    () => ({ personas, addPersonas, refresh, isLoading }),
    [personas, addPersonas, refresh, isLoading]
  );

  return (
    <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>
  );
}

export function usePersonas() {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error('usePersonas must be used within PersonaProvider');
  return ctx;
}
