"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export default function PublishPage() {
    const [platforms, setPlatforms] = React.useState({
        twitter: false,
        linkedin: false,
    });
    const [isScheduled, setIsScheduled] = React.useState(false);

    const togglePlatform = (platform: "twitter" | "linkedin") => {
        setPlatforms((prev) => ({ ...prev, [platform]: !prev[platform] }));
    };

    const handleSchedule = () => {
        setIsScheduled(true);
        // Simulate API call
        console.log("Scheduling posts to:", platforms);
    };

    if (isScheduled) {
        return (
            <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center p-8 text-center">
                <div className="mb-4 rounded-full bg-green-100 p-4 text-green-600">
                    <svg
                        width="32"
                        height="32"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >
                        <polyline points="20 6 9 17 4 12" />
                    </svg>
                </div>
                <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
                    All set!
                </h1>
                <p className="mt-2 max-w-md text-zinc-600">
                    Your content has been successfully scheduled. Sit back and watch your
                    audience grow.
                </p>
                <Button
                    className="mt-8"
                    variant="outline"
                    onClick={() => setIsScheduled(false)}
                >
                    Schedule More
                </Button>
            </div>
        );
    }

    return (
        <div className="flex min-h-[calc(100vh-4rem)] flex-col pb-24">
            <div className="py-8">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
                    Ready to Publish
                </h1>
                <p className="mt-2 text-zinc-600">
                    Connect your accounts and schedule your content.
                </p>
            </div>

            <div className="space-y-6">
                <div className="rounded-lg border bg-white p-6 shadow-sm">
                    <h2 className="text-lg font-semibold text-zinc-900">
                        Connect Platforms
                    </h2>
                    <div className="mt-6 space-y-4">
                        {/* Twitter */}
                        <div className="flex items-center justify-between rounded-md border p-4">
                            <div className="flex items-center gap-4">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-500 text-white">
                                    <svg
                                        width="20"
                                        height="20"
                                        viewBox="0 0 24 24"
                                        fill="currentColor"
                                    >
                                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                                    </svg>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-zinc-900">Twitter / X</span>
                                        {platforms.twitter && (
                                            <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                                                Connected
                                            </Badge>
                                        )}
                                    </div>
                                    <p className="text-sm text-zinc-500">
                                        Post tweets and threads
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant={platforms.twitter ? "outline" : "secondary"}
                                onClick={() => togglePlatform("twitter")}
                            >
                                {platforms.twitter ? "Disconnect" : "Connect"}
                            </Button>
                        </div>

                        {/* LinkedIn */}
                        <div className="flex items-center justify-between rounded-md border p-4">
                            <div className="flex items-center gap-4">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-700 text-white">
                                    <svg
                                        width="20"
                                        height="20"
                                        viewBox="0 0 24 24"
                                        fill="currentColor"
                                    >
                                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                                    </svg>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-zinc-900">LinkedIn</span>
                                        {platforms.linkedin && (
                                            <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                                                Connected
                                            </Badge>
                                        )}
                                    </div>
                                    <p className="text-sm text-zinc-500">
                                        Share professional updates
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant={platforms.linkedin ? "outline" : "secondary"}
                                onClick={() => togglePlatform("linkedin")}
                            >
                                {platforms.linkedin ? "Disconnect" : "Connect"}
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 border-t bg-white p-4 shadow-lg md:pl-72 lg:pl-0">
                <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                    <div className="text-sm text-zinc-500">
                        {!platforms.twitter && !platforms.linkedin
                            ? "Connect a platform to continue"
                            : "Ready to launch"}
                    </div>
                    <Button
                        onClick={handleSchedule}
                        disabled={!platforms.twitter && !platforms.linkedin}
                    >
                        Schedule All Posts
                    </Button>
                </div>
            </div>
        </div>
    );
}
