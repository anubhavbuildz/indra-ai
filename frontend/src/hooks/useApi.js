import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../services/api";

export function useAssessments(options = {}) {
  return useQuery({
    queryKey: ["assessments", options],
    queryFn: () => api.assessments(options),
    staleTime: 20_000,
  });
}

export function useAssessment(id) {
  return useQuery({
    queryKey: ["assessment", id],
    queryFn: () => api.assessment(id),
    enabled: Boolean(id),
  });
}

export function useRagStatus(enabled = true) {
  return useQuery({
    queryKey: ["rag-status"],
    queryFn: api.ragStatus,
    enabled,
    staleTime: 60_000,
    retry: false,
  });
}

export function useBackendHealth() {
  return useQuery({
    queryKey: ["backend-health"],
    queryFn: api.health,
    staleTime: 30_000,
    retry: false,
  });
}

export function useAwsIdentity(enabled = true) {
  return useQuery({
    queryKey: ["aws-identity"],
    queryFn: api.awsIdentity,
    enabled,
    staleTime: 60_000,
    retry: false,
  });
}

export function useLatestAudit() {
  return useQuery({
    queryKey: ["latest-audit"],
    queryFn: () => Promise.resolve(null),
    enabled: false,
  });
}

export function useChatMutation() {
  return useMutation({ mutationFn: ({ message, history }) => api.chat(message, history) });
}
