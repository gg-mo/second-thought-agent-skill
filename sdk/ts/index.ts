export type ProposalType = "idea" | "decision" | "design" | "plan" | "action" | "tool_call" | "response";
export type RiskLevel = "low" | "medium" | "high";
export type Stage = "brainstorming" | "convergence" | "pre_execution" | "post_feedback";
export type CritiqueMode = "strict" | "fast";
export type ExplainabilityMode = "compact" | "standard" | "detailed";
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
  explainability?: ExplainabilityMode;
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

const STATUSS = ["proceed", "revise", "prompt_human"];
const PROPOSAL_TYPES = ["idea", "decision", "design", "plan", "action", "tool_call", "response"];
const RISK_LEVELS = ["low", "medium", "high"];
const STAGES = ["brainstorming", "convergence", "pre_execution", "post_feedback"];

function isString(x: unknown): x is string {
  return typeof x === "string";
}

function isStringArray(x: unknown): x is string[] {
  return Array.isArray(x) && x.every(isString);
}

export function validateCritiqueInput(value: unknown): value is CritiqueInput {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;

  if (!isString(v.original_intent) || !v.original_intent.trim()) return false;
  if (!isString(v.current_context) || !v.current_context.trim()) return false;
  if (!isString(v.proposal) || !v.proposal.trim()) return false;
  if (!isString(v.rationale) || !v.rationale.trim()) return false;

  if (!isString(v.proposal_type) || !PROPOSAL_TYPES.includes(v.proposal_type)) return false;
  if (v.risk_level !== undefined && (!isString(v.risk_level) || !RISK_LEVELS.includes(v.risk_level))) return false;
  if (v.stage !== undefined && (!isString(v.stage) || !STAGES.includes(v.stage))) return false;
  if (v.constraints !== undefined && !isStringArray(v.constraints)) return false;

  return true;
}

export function validateCritiqueOutput(value: unknown): value is CritiqueOutput {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;

  if (!isString(v.status) || !STATUSS.includes(v.status)) return false;
  if (!isString(v.summary)) return false;
  if (!isString(v.goal_alignment)) return false;
  if (!isStringArray(v.concerns)) return false;
  if (!isStringArray(v.assumptions)) return false;
  if (!isStringArray(v.better_options)) return false;
  if (!isString(v.challenge_prompt)) return false;
  if (!isString(v.recommended_next_step)) return false;
  if (!(v.prompt_to_human === null || isString(v.prompt_to_human))) return false;
  if (typeof v.confidence !== "number" || v.confidence < 0 || v.confidence > 1) return false;
  if (!isStringArray(v.decision_factors)) return false;

  return true;
}

export async function critiqueViaHttp(input: CritiqueInput, endpoint: string): Promise<CritiqueOutput> {
  if (!validateCritiqueInput(input)) {
    throw new Error("Invalid critique input shape");
  }

  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    throw new Error(`Critique request failed: ${res.status}`);
  }

  const data: unknown = await res.json();
  if (!validateCritiqueOutput(data)) {
    throw new Error("Invalid critique output shape");
  }
  return data;
}
