

export default function Home() {
  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center space-y-8 text-center">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tight text-zinc-900 sm:text-6xl">
          Video Repurposing
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-zinc-600">
          Transform your long-form videos into engaging short-form content with AI.
        </p>
      </div>
    </div>
  );
}
