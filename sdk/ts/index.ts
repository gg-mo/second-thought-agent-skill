export type ProposalType = "idea" | "decision" | "design" | "plan" | "action" | "tool_call" | "response";
export type RiskLevel = "low" | "medium" | "high";
export type Stage = "brainstorming" | "convergence" | "pre_execution" | "post_feedback";
export type CritiqueMode = "strict" | "fast";
export type CritiqueStatus = "proceed" | "revise" | "prompt_human";

export interface CritiqueInput {
  original_intent: string;
  current_context: string;
  proposal_type: ProposalType;
  proposal: string;
  rationale: string;
  constraints?: string[];
  risk_level?: RiskLevel;
  stage?: Stage;
  should_challenge?: boolean;
  mode?: CritiqueMode;
  reversibility?: "reversible" | "partially_reversible" | "irreversible" | "unknown";
  estimated_cost?: "low" | "medium" | "high" | "unknown";
  blast_radius?: "local" | "team" | "org" | "public" | "unknown";
}

export interface CritiqueOutput {
  status: CritiqueStatus;
  summary: string;
  goal_alignment: string;
  concerns: string[];
  assumptions: string[];
  better_options: string[];
  challenge_prompt: string;
  recommended_next_step: string;
  prompt_to_human: string | null;
  confidence: number;
  decision_factors: string[];
}

export function isCritiqueOutput(value: unknown): value is CritiqueOutput {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.status === "string" &&
    typeof v.summary === "string" &&
    Array.isArray(v.concerns) &&
    Array.isArray(v.decision_factors)
  );
}

export async function critiqueViaHttp(input: CritiqueInput, endpoint: string): Promise<CritiqueOutput> {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    throw new Error(`Critique request failed: ${res.status}`);
  }

  const data: unknown = await res.json();
  if (!isCritiqueOutput(data)) {
    throw new Error("Invalid critique output shape");
  }
  return data;
}
