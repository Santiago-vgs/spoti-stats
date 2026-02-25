import useSWR from "swr";
import { fetcher } from "./api";
import { AuthStatus } from "./types";

export function useAuth() {
  const { data, error, isLoading, mutate } = useSWR<AuthStatus>(
    "/auth/status",
    fetcher<AuthStatus>("/auth/status"),
    { revalidateOnFocus: true }
  );

  return {
    authenticated: data?.authenticated ?? false,
    isLoading,
    error,
    mutate,
  };
}
