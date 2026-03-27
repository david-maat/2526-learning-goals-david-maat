export type Track = "APP" | "AI" | "CCS" | "DI" | "EVERYTHING";
export type Status = "" | "Todo" | "In Progress" | "Done" | "Verified";
export type EvidenceFilterMode = "all" | "with_evidence" | "without_evidence";

export interface LearningGoalData {
    number: string;
    title: string;
    track: Track[];
    status: Status;
    project: string[];
}

export interface LearningGoal extends LearningGoalData {
    category: string;
    categoryNumber: number;
    evidencePath: string;
    hasEvidence: boolean;
    verified: string;
}

export interface Category {
    number: number;
    name: string;
    goals: LearningGoal[];
}
