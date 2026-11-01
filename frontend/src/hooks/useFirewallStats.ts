import { useEffect, useState } from "react";

import { fetchStats } from "../services/api";
import type { FirewallStats } from "../types";

export function useFirewallStats() {
  const [stats, setStats] = useState<FirewallStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchStats()
      .then((data) => {
        if (active) {
          setStats(data);
          setError(null);
        }
      })
      .catch((err: Error) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return { stats, loading, error };
}
