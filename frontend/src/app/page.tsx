"use client";

import { FormEvent, useState } from "react";

type PageResult = {
url: string;
title: string;
text: string;
characters: number;
depth: number;
};

type AnalyzeResponse = {
success: boolean;
session_id: string;
url: string;
pages_crawled: number;
pages_failed: number;
total_characters: number;
pages: PageResult[];
};

type Source = {
url: string;
title: string;
evidence: string;
score: number;
};

type AskResponse = {
answer: string;
sources: Source[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
const [url, setUrl] = useState("");
const [question, setQuestion] = useState("");

const [sessionId, setSessionId] = useState<string | null>(null);
const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
const [result, setResult] = useState<AskResponse | null>(null);

const [analyzing, setAnalyzing] = useState(false);
const [asking, setAsking] = useState(false);
const [error, setError] = useState("");

async function analyzeWebsite(event: FormEvent) {
event.preventDefault();


if (!url.trim()) {
  setError("Enter a website URL first.");
  return;
}

setAnalyzing(true);
setError("");
setResult(null);
setSessionId(null);
setAnalysis(null);

try {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: url.trim(),
    }),
  });

  if (!response.ok) {
    throw new Error("Website analysis failed.");
  }

  const data: AnalyzeResponse = await response.json();

  setAnalysis(data);
  setSessionId(data.session_id);
} catch (err) {
  setError(
    err instanceof Error
      ? err.message
      : "Unable to analyze the website.",
  );
} finally {
  setAnalyzing(false);
}


}

async function askQuestion(event: FormEvent) {
event.preventDefault();


if (!sessionId) {
  setError("Analyze a website before asking a question.");
  return;
}

if (!question.trim()) {
  setError("Enter a question first.");
  return;
}

setAsking(true);
setError("");

try {
  const response = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      question: question.trim(),
    }),
  });

  if (!response.ok) {
    throw new Error("Question processing failed.");
  }

  const data: AskResponse = await response.json();

  setResult(data);
} catch (err) {
  setError(
    err instanceof Error
      ? err.message
      : "Unable to answer the question.",
  );
} finally {
  setAsking(false);
}


}

function resetWorkspace() {
setUrl("");
setQuestion("");
setSessionId(null);
setAnalysis(null);
setResult(null);
setError("");
}



return ( <main suppressHydrationWarning className="min-h-screen bg-[#fafafa] text-zinc-950"> <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 sm:px-8">
{/* NAVBAR */} <header className="flex h-20 items-center justify-between border-b border-zinc-200"> <div className="flex items-center gap-3"> <div className="grid size-8 place-items-center rounded-lg bg-zinc-950 text-white"> <span className="text-sm font-bold">W</span> </div>

        <div>
          <div className="text-sm font-semibold tracking-tight">
            Website QA
          </div>
          <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-400">
            Retrieval Engine
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-zinc-500">
        <span
          className={`size-1.5 rounded-full ${
            analyzing || asking
              ? "animate-pulse bg-amber-500"
              : "bg-emerald-500"
          }`}
        />
        {analyzing || asking ? "PROCESSING" : "SYSTEM ONLINE"}
      </div>
    </header>

    {/* HERO */}
    <section className="flex flex-col items-center pb-12 pt-20 text-center sm:pt-28">
      <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.16em] text-zinc-500 shadow-sm">
        <span className="size-1.5 rounded-full bg-emerald-500" />
        Deterministic web intelligence
      </div>

      <h1 className="max-w-4xl text-4xl font-semibold tracking-[-0.045em] sm:text-6xl lg:text-7xl">
        Ask any website
        <br />
        <span className="text-zinc-400">anything.</span>
      </h1>

      <p className="mt-6 max-w-xl text-sm leading-6 text-zinc-500 sm:text-base">
        Analyze a website, index its content, and ask questions using
        answers grounded directly in the pages it contains.
      </p>
    </section>

    {/* WORKSPACE */}
    <section className="mx-auto w-full max-w-3xl pb-20">
      {/* URL INPUT */}
      <form onSubmit={analyzeWebsite}>
        <label className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-zinc-500">
          Website URL
        </label>

        <div className="group flex min-h-14 items-center rounded-xl border border-zinc-300 bg-white p-1.5 shadow-[0_1px_2px_rgba(0,0,0,0.04)] transition focus-within:border-zinc-500 focus-within:ring-4 focus-within:ring-zinc-100">
          <div className="pl-3 text-zinc-400">
            <svg
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M3 12h18M12 3c2.2 2.5 3.3 5.5 3.3 9s-1.1 6.5-3.3 9c-2.2-2.5-3.3-6.5-3.3-9S9.8 5.5 12 3Z" />
            </svg>
          </div>

          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://example.com"
            className="min-w-0 flex-1 bg-transparent px-3 text-sm outline-none placeholder:text-zinc-400"
            disabled={analyzing}
          />

          <button
            type="submit"
            disabled={analyzing}
            className="inline-flex h-11 items-center gap-2 rounded-lg bg-zinc-950 px-5 text-xs font-semibold text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <span className="size-3 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Analyzing
              </>
            ) : (
              <>
                Analyze
                <span>↗</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* ERROR */}
      {error && (
        <div className="mt-4 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <span className="font-semibold">!</span>
          <span>{error}</span>
        </div>
      )}

      {/* ANALYSIS STATUS */}
      {analysis && (
        <div className="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-100 px-5 py-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-400">
                Website indexed
              </div>

              <div className="mt-1 max-w-md truncate text-sm font-medium">
                {analysis.url}
              </div>
            </div>

            <button
              type="button"
              onClick={resetWorkspace}
              className="text-xs font-medium text-zinc-400 transition hover:text-zinc-950"
            >
              New website
            </button>
          </div>

          <div className="grid grid-cols-3 divide-x divide-zinc-100">
            <Metric
              label="Pages"
              value={analysis.pages_crawled}
            />
            <Metric
              label="Characters"
              value={analysis.total_characters.toLocaleString()}
            />
            <Metric
              label="Failed"
              value={analysis.pages_failed}
            />
          </div>
        </div>
      )}

      {/* QUESTION */}
      {sessionId && (
        <form
          onSubmit={askQuestion}
          className="mt-8"
        >
          <label className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-zinc-500">
            Ask a question
          </label>

          <div className="rounded-xl border border-zinc-300 bg-white p-2 shadow-sm transition focus-within:border-zinc-500 focus-within:ring-4 focus-within:ring-zinc-100">
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="What is this website about?"
              rows={3}
              disabled={asking}
              className="w-full resize-none bg-transparent px-3 py-2 text-sm leading-6 outline-none placeholder:text-zinc-400"
            />

            <div className="flex items-center justify-between border-t border-zinc-100 px-2 pt-2">
              <span className="px-2 text-[11px] text-zinc-400">
                Answers are generated only from indexed content.
              </span>

              <button
                type="submit"
                disabled={asking}
                className="inline-flex h-10 items-center gap-2 rounded-lg bg-zinc-950 px-5 text-xs font-semibold text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {asking ? (
                  <>
                    <span className="size-3 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Searching
                  </>
                ) : (
                  <>
                    Ask question
                    <span>→</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      )}

      {/* ANSWER */}
      {result && (
        <section className="mt-12">
          <div className="mb-3 flex items-center justify-between">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-zinc-400">
              Answer
            </div>

            <div className="text-[11px] text-zinc-400">
              {result.sources.length}{" "}
              {result.sources.length === 1
                ? "source"
                : "sources"}
            </div>
          </div>

          <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-7">
            <p className="text-base leading-8 text-zinc-800">
              {result.answer}
            </p>
          </div>

          {/* SOURCES */}
          {result.sources.length > 0 && (
            <div className="mt-8">
              <div className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-zinc-400">
                Sources
              </div>

              <div className="space-y-3">
                {result.sources.map((source, index) => (
                  <article
                    key={`${source.url}-${index}`}
                    className="rounded-xl border border-zinc-200 bg-white p-5 transition hover:border-zinc-300 hover:shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <h3 className="truncate text-sm font-semibold">
                          {source.title}
                        </h3>

                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-1 block truncate text-xs text-zinc-400 transition hover:text-zinc-700"
                        >
                          {source.url}
                        </a>
                      </div>

                      <div className="shrink-0 rounded-md bg-zinc-100 px-2 py-1 text-[10px] font-semibold tabular-nums text-zinc-600">
                        {(source.score * 100).toFixed(1)}%
                      </div>
                    </div>

                    <div className="mt-4 border-l-2 border-zinc-200 pl-4 text-sm leading-6 text-zinc-600">
                      {source.evidence}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>
      )}
    </section>

    {/* FOOTER */}
    <footer className="mt-auto flex flex-col items-center justify-between gap-3 border-t border-zinc-200 py-6 text-[11px] text-zinc-400 sm:flex-row">
      <span>Website QA Engine</span>

      <span>
        Retrieval · Ranking · Evidence · Citations
      </span>
    </footer>
  </div>
</main>


);
}

function Metric({
label,
value,
}: {
label: string;
value: string | number;
}) {
return ( <div className="px-5 py-4"> <div className="text-[10px] font-medium uppercase tracking-[0.14em] text-zinc-400">
{label} </div>

  <div className="mt-1 text-lg font-semibold tracking-tight">
    {value}
  </div>
</div>


);
}
