"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchJson } from "@/lib/api";
import { DeploymentTicket } from "@/lib/types";

function formatDate(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

export function TicketsPanel() {
  const [tickets, setTickets] = useState<DeploymentTicket[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const loadTickets = useCallback(async () => {
    try {
      setStatus("loading");
      setError(null);
      const data = await fetchJson<DeploymentTicket[]>("/api/tickets");
      setTickets(data);
      setStatus("idle");
    } catch (err) {
      console.error("Failed to load tickets", err);
      setError(err instanceof Error ? err.message : "Unknown error");
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const activeTickets = useMemo(
    () => tickets.filter((ticket) => ticket.status !== "closed"),
    [tickets],
  );

  return (
    <section className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl w-full max-w-4xl p-8">
      <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-widest text-gray-500">Terraform Agent Tickets</p>
          <h2 className="text-3xl font-semibold text-gray-900">
            {activeTickets.length} active ticket{activeTickets.length === 1 ? "" : "s"}
          </h2>
          <p className="text-gray-600 text-sm">
            Monitoring {tickets.length} total ticket{tickets.length === 1 ? "" : "s"}
          </p>
        </div>
        <button
          onClick={loadTickets}
          className="mt-4 inline-flex items-center justify-center rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 md:mt-0"
        >
          {status === "loading" ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error} — please ensure the FastAPI server is running on {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}.
        </div>
      )}

      <div className="mt-6 grid gap-4">
        {tickets.length === 0 && status !== "loading" ? (
          <p className="text-center text-gray-600">
            No tickets yet. Use the AG-UI endpoint or `/api/chat` to create one, then refresh this panel.
          </p>
        ) : (
          tickets.map((ticket) => (
            <article key={ticket.ticket_id} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{ticket.intent_summary || ticket.ticket_id}</h3>
                  <p className="text-sm text-gray-500">
                    Requested by {ticket.requested_by} · Workspace {ticket.terraform_workspace}
                  </p>
                </div>
                <span className="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-600 uppercase">
                  {ticket.status.replace(/_/g, " ")}
                </span>
              </div>
              <dl className="mt-4 grid gap-4 md:grid-cols-3">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500">Current Stage</dt>
                  <dd className="text-sm font-medium text-gray-900">{ticket.current_stage}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500">Environment</dt>
                  <dd className="text-sm font-medium text-gray-900">{ticket.environment}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500">Last Updated</dt>
                  <dd className="text-sm font-medium text-gray-900">{formatDate(ticket.updated_at)}</dd>
                </div>
              </dl>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
