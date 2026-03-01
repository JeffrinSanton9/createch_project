// src/lib/simulationApi.js
// Utility functions for simulation API endpoints

const BASE = "http://localhost:8000/api/precast";

export async function getSignals() {
    const res = await fetch(`${BASE}/signals`);
    if (!res.ok) throw new Error("Failed to fetch signals");
    return res.json();
}

export async function evaluateScenario(scenario) {
    const res = await fetch(`${BASE}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(scenario)
    });
    if (!res.ok) throw new Error("Failed to evaluate scenario");
    return res.json();
}

export async function predictTime(input) {
    const res = await fetch(`${BASE}/predict/time`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input)
    });
    if (!res.ok) throw new Error("Failed to predict time");
    return res.json();
}

export async function predictCost(input) {
    const res = await fetch(`${BASE}/predict/cost`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input)
    });
    if (!res.ok) throw new Error("Failed to predict cost");
    return res.json();
}

export async function getSensitivity(signal, input) {
    const res = await fetch(`${BASE}/sensitivity/${signal}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input)
    });
    if (!res.ok) throw new Error("Failed to get sensitivity");
    return res.json();
}
