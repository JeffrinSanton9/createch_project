// src/lib/approximationApi.js
export async function fetchApproximation(points, method = "linear", degree = 2) {
    const res = await fetch("http://localhost:8000/api/approximation/fit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points, method, degree })
    });
    if (!res.ok) throw new Error("Failed to fetch approximation");
    return res.json();
}
