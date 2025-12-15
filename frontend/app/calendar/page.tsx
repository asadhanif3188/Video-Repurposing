"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useRouter } from "next/navigation";

interface CalendarItem {
    day: number;
    date: string;
    platform: "twitter" | "linkedin" | null;
    preview: string;
}

// Generate 30 days of mock data
const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const generateMockData = (): CalendarItem[] => {
    return Array.from({ length: 30 }, (_, i) => {
        const day = i + 1;
        let platform: "twitter" | "linkedin" | null = null;
        let preview = "";

        // Differentiate content randomly for demo
        if (day % 3 === 0) {
            platform = "twitter";
            preview = "🚀 New feature alert! Check out...";
        } else if (day % 5 === 0) {
            platform = "linkedin";
            preview = "Reflecting on leadership lessons...";
        }

        return {
            day,
            date: `2025-12-${String(day).padStart(2, "0")}`,
            platform,
            preview,
        };
    });
};

const CALENDAR_ITEMS = generateMockData();

export default function CalendarPage() {
    const router = useRouter();
    const handleScheduleAll = () => {
        const itemsToSchedule = CALENDAR_ITEMS.filter((i) => i.platform);
        console.log(`Scheduling ${itemsToSchedule.length} items...`);
        router.push("/publish");
    };

    return (
        <div className="flex min-h-[calc(100vh-4rem)] flex-col pb-24">
            <div className="py-8">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
                    Content Calendar
                </h1>
                <p className="mt-2 text-zinc-600">
                    Preview and schedule your upcoming content.
                </p>
            </div>

            <div className="rounded-lg border bg-white shadow-sm">
                {/* Days Header */}
                <div className="grid grid-cols-7 border-b bg-zinc-50">
                    {DAYS_OF_WEEK.map((day) => (
                        <div
                            key={day}
                            className="py-2 text-center text-sm font-semibold text-zinc-700"
                        >
                            {day}
                        </div>
                    ))}
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7">
                    {CALENDAR_ITEMS.map((item, index) => (
                        <div
                            key={item.day}
                            className={`min-h-[120px] border-b border-r p-2 transition-colors ${index % 7 === 6 ? "border-r-0" : ""
                                } ${item.platform ? "bg-white" : "bg-zinc-50/30"}`}
                        >
                            <div className="mb-2 text-xs font-medium text-zinc-500">
                                {item.day}
                            </div>
                            {item.platform && (
                                <div className="flex flex-col gap-2">
                                    <Badge
                                        variant={
                                            item.platform === "twitter" ? "twitter" : "linkedin"
                                        }
                                        className="w-fit scale-90 px-1.5 py-0"
                                    >
                                        {item.platform === "twitter" ? "X" : "LI"}
                                    </Badge>
                                    <p className="line-clamp-3 text-xs text-zinc-700">
                                        {item.preview}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 border-t bg-white p-4 shadow-lg md:pl-72 lg:pl-0">
                <div className="mx-auto flex max-w-7xl items-center justify-end px-4 sm:px-6 lg:px-8">
                    <Button onClick={handleScheduleAll}>Schedule All</Button>
                </div>
            </div>
        </div>
    );
}
