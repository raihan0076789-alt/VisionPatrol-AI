export type UserRole = "admin" | "operator" | "viewer";
export type ViolationType = "helmet" | "triple_riding" | "signal_jump" | "wrong_side" | "no_plate" | "over_speed";
export type ViolationStatus = "pending" | "confirmed" | "dismissed" | "challan_issued";
export type ChallanStatus = "generated" | "served" | "paid" | "cancelled" | "disputed";

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Violation {
  id: string;
  violation_type: ViolationType;
  status: ViolationStatus;
  confidence_score: number;
  plate_number: string | null;
  location: string | null;
  detected_at: string;
  notes: string | null;
}

export interface Challan {
  id: string;
  challan_number: string;
  fine_amount: number;
  status: ChallanStatus;
  due_date: string | null;
  created_at: string;
  pdf_path: string | null;
}

export interface AnalyticsSummary {
  today_violations: number;
  total_violations: number;
  pending_violations: number;
  total_challans: number;
  fines_collected: number;
}