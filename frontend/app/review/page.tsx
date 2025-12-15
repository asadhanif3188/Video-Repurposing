"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Switch } from "@/components/ui/Switch";
import { Textarea } from "@/components/ui/Textarea";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";

interface Post {
    id: string; // Schedule ID matching backend
    platform: "twitter" | "linkedin";
    content: string;
    included: boolean;
    date?: string;
}

function ReviewContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const id = searchParams.get("id");

    const [posts, setPosts] = React.useState<Post[]>([]);
    const [status, setStatus] = React.useState<string>("loading"); // loading, processing, ready, error
    const [loadingMessage, setLoadingMessage] = React.useState("Initializing...");
    const [publishing, setPublishing] = React.useState(false);

    // Polling Logic
    React.useEffect(() => {
        if (!id) return;

        let isActive = true;
        let timeoutId: NodeJS.Timeout;

        const fetchSchedule = async () => {
            try {
                // Trigger Schedule Generation
                await api.scheduleContent(id);

                // Fetch Preview
                const previewItems = await api.getSchedulePreview(id);

                // Map to UI model
                const mappedPosts: Post[] = previewItems.map((item: { id: string; platform: "twitter" | "linkedin"; preview: string; date: string }) => ({
                    id: item.id,
                    platform: item.platform,
                    content: item.preview,
                    included: true,
                    date: item.date
                }));

                if (isActive) {
                    setPosts(mappedPosts);
                    setStatus("ready");
                }
            } catch (err) {
                console.error("Failed to fetch schedule", err);
                if (isActive) {
                    setStatus("error");
                    setLoadingMessage("Failed to generate schedule.");
                }
            }
        };

        const poll = async () => {
            if (!isActive) return;

            try {
                const statusData = await api.getContentStatus(id);

                if (statusData.status === "completed") {
                    setLoadingMessage("Generating Schedule...");
                    await fetchSchedule();
                    return; // Stop polling
                }

                if (statusData.status === "failed") {
                    setStatus("error");
                    setLoadingMessage(`Generation Failed: ${statusData.error || "Unknown error"}`);
                    return; // Stop polling
                }

                // Still processing
                setStatus("processing");
                setLoadingMessage("AI is watching the video and generating content atoms...");

                // Schedule next poll
                if (isActive) {
                    timeoutId = setTimeout(poll, 2000);
                }

            } catch (error) {
                console.error(error);
                // Retry on error
                if (isActive) timeoutId = setTimeout(poll, 5000);
            }
        };

        poll();

        return () => {
            isActive = false;
            clearTimeout(timeoutId);
        };
    }, [id]);


    const handleToggleInclude = (postId: string, checked: boolean) => {
        setPosts((prev) =>
            prev.map((post) =>
                post.id === postId ? { ...post, included: checked } : post
            )
        );
    };

    const handlePublish = async () => {
        if (!id) return;
        setPublishing(true);
        try {
            const result = await api.runSchedule(id);
            console.log("Publish result:", result);
            alert(`Successfully published ${result.published_count} posts!`);
            router.push("/dashboard");
        } catch (error) {
            console.error(error);
            alert("Failed to publish content.");
        } finally {
            setPublishing(false);
        }
    };

    if (!id) {
        return <div className="p-12 text-center">Invalid ID</div>;
    }

    if (status === "processing" || status === "loading") {
        return (
            <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center space-y-4">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-900" />
                <p className="text-zinc-600">{loadingMessage}</p>
            </div>
        );
    }

    if (status === "error") {
        return (
            <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center space-y-4">
                <p className="text-red-500 font-bold">Error</p>
                <p className="text-zinc-600">{loadingMessage}</p>
                <Button onClick={() => router.push("/dashboard")}>Back to Dashboard</Button>
            </div>
        );
    }

    const selectedCount = posts.filter((p) => p.included).length;

    return (
        <div className="flex min-h-[calc(100vh-4rem)] flex-col pb-24">
            <div className="py-8">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
                    Review Schedule
                </h1>
                <p className="mt-2 text-zinc-600">
                    Review the generated schedule and publish.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {posts.map((post) => (
                    <div
                        key={post.id}
                        className={`flex flex-col rounded-lg border bg-white shadow-sm transition-opacity ${!post.included ? "opacity-60 grayscale-[0.5]" : ""
                            }`}
                    >
                        <div className="flex items-center justify-between border-b p-4">
                            <div className="flex items-center gap-2">
                                <Badge
                                    variant={post.platform === "twitter" ? "twitter" : "linkedin"}
                                >
                                    {post.platform === "twitter" ? "Twitter / X" : "LinkedIn"}
                                </Badge>
                                <span className="text-xs text-gray-500">{post.date}</span>
                            </div>
                            <Switch
                                checked={post.included}
                                onCheckedChange={(checked) =>
                                    handleToggleInclude(post.id, checked)
                                }
                            />
                        </div>
                        <div className="flex-1 p-4">
                            <Textarea
                                className="min-h-[200px] resize-none border-0 p-0 focus-visible:ring-0"
                                value={post.content}
                                readOnly // Editing not supported in this MVP version backend-sync wise
                            />
                        </div>
                    </div>
                ))}
            </div>

            <div className="fixed bottom-0 left-0 right-0 border-t bg-white p-4 shadow-lg md:pl-72 lg:pl-0">
                <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                    <div className="text-sm font-medium text-zinc-600">
                        {selectedCount} item{selectedCount !== 1 && "s"} scheduled
                    </div>
                    <Button onClick={handlePublish} disabled={selectedCount === 0 || publishing}>
                        {publishing ? "Publishing..." : "Run Schedule"}
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default function ReviewPage() {
    return (
        <React.Suspense fallback={<div className="p-12 text-center">Loading...</div>}>
            <ReviewContent />
        </React.Suspense>
    );
}
