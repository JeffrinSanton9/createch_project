// src/lib/api.js
// API utility for frontend to interact with FastAPI backend

export async function createProject(data) {
    const res = await fetch("http://localhost:8000/api/projects/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create project");
    return res.json();
}

export async function getProject(id) {
    const res = await fetch(`http://localhost:8000/api/projects/${id}`);
    if (!res.ok) throw new Error("Failed to fetch project");
    return res.json();
}

export async function updateProject(id, data) {
    const res = await fetch(`http://localhost:8000/api/projects/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update project");
    return res.json();
}

export async function deleteElement(projectId, elementId) {
    const res = await fetch(`http://localhost:8000/api/projects/${projectId}/elements/${elementId}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete element");
    return true;
}
