"use client";

import * as React from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function DashboardPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = React.useState(false);
    const [formData, setFormData] = React.useState({
        url: "",
        tone: "Professional",
        emoji: "None",
    });
    const [errors, setErrors] = React.useState<{ url?: string; api?: string }>({});

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        if (name === "url") {
            setErrors((prev) => ({ ...prev, url: undefined }));
        }
        setErrors((prev) => ({ ...prev, api: undefined }));
    };

    const validateUrl = (url: string) => {
        // Basic YouTube URL regex
        const regex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
        return regex.test(url);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validateUrl(formData.url)) {
            setErrors({ url: "Please enter a valid YouTube URL" });
            return;
        }

        setIsLoading(true);
        setErrors({});

        try {
            const result = await api.createContent({
                url: formData.url,
                tone: formData.tone,
                emoji_usage: formData.emoji,
            });
            console.log("Job Created:", result);
            router.push(`/review?id=${result.id}`);
        } catch (error: unknown) {
            const err = error as { error?: string };
            console.error("API Error:", error);
            let message = "Failed to create content job. Please try again.";

            if (err?.error === "TRANSCRIPT_NOT_AVAILABLE") {
                message = "This video does not have captions enabled.";
            } else if (err?.error === "TRANSCRIPT_ACCESS_DENIED") {
                message = "This video cannot be processed due to access restrictions.";
            }

            setErrors({ api: message });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center py-12">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
                        Create content from YouTube
                    </h1>
                    <p className="mt-2 text-sm text-zinc-600">
                        Enter a video URL to generate engaging content.
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="mt-8 space-y-6">
                    <div className="space-y-4">
                        <div>
                            <label
                                htmlFor="url"
                                className="block text-sm font-medium text-zinc-900"
                            >
                                YouTube URL
                            </label>
                            <div className="mt-1">
                                <Input
                                    id="url"
                                    name="url"
                                    type="text"
                                    placeholder="https://youtube.com/watch?v=..."
                                    value={formData.url}
                                    onChange={handleChange}
                                    className={errors.url ? "border-red-500 focus-visible:ring-red-500" : ""}
                                />
                                {errors.url && (
                                    <p className="mt-1 text-xs text-red-500">{errors.url}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label
                                htmlFor="tone"
                                className="block text-sm font-medium text-zinc-900"
                            >
                                Tone
                            </label>
                            <div className="mt-1">
                                <Select
                                    id="tone"
                                    name="tone"
                                    value={formData.tone}
                                    onChange={handleChange}
                                >
                                    <option value="Professional">Professional</option>
                                    <option value="Casual">Casual</option>
                                    <option value="Bold">Bold</option>
                                </Select>
                            </div>
                        </div>

                        <div>
                            <label
                                htmlFor="emoji"
                                className="block text-sm font-medium text-zinc-900"
                            >
                                Emoji Usage
                            </label>
                            <div className="mt-1">
                                <Select
                                    id="emoji"
                                    name="emoji"
                                    value={formData.emoji}
                                    onChange={handleChange}
                                >
                                    <option value="None">None</option>
                                    <option value="Light">Light</option>
                                    <option value="Medium">Medium</option>
                                </Select>
                            </div>
                        </div>

                        {errors.api && (
                            <p className="text-sm text-red-500 text-center">{errors.api}</p>
                        )}
                    </div>

                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? "Generating..." : "Generate Content"}
                    </Button>
                </form>
            </div>
        </div>
    );
}
