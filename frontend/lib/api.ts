const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
    createContent: async (payload: { url: string; tone: string; emoji_usage: string }) => {
        const response = await fetch(`${API_URL}/api/v1/content/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch {
                // If JSON parse fails, fall back to status text
            }
            throw errorData || new Error("Failed to create content job");
        }
        return response.json();
    },

    getContentStatus: async (transcriptId: string) => {
        const response = await fetch(`${API_URL}/api/v1/content/status/${transcriptId}`);
        if (!response.ok) {
            throw new Error("Failed to fetch status");
        }
        return response.json();
    },

    scheduleContent: async (transcriptId: string) => {
        const response = await fetch(`${API_URL}/api/v1/content/schedule/${transcriptId}`, {
            method: "POST",
        });
        if (!response.ok) {
            throw new Error("Failed to schedule content");
        }
        return response.json();
    },

    getSchedulePreview: async (transcriptId: string) => {
        const response = await fetch(`${API_URL}/api/v1/content/schedule/preview/${transcriptId}`);
        if (!response.ok) {
            throw new Error("Failed to fetch schedule preview");
        }
        return response.json();
    },

    runSchedule: async (transcriptId: string) => {
        const response = await fetch(`${API_URL}/api/v1/content/schedule/run/${transcriptId}`, {
            method: "POST",
        });
        if (!response.ok) {
            throw new Error("Failed to run schedule simulation");
        }
        return response.json();
    }
};
