"use client";
import { useEffect, useState } from "react";
import NavBar from "@/app/components/Navibar.jsx";
import Link from "next/link";

export default function ProjectsPage() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch("http://localhost:8000/api/projects/")
            .then((res) => res.json())
            .then(setProjects)
            .catch((err) => setError("Failed to load projects"))
            .finally(() => setLoading(false));
    }, []);

    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl mt-10 text-center text-gray-900">
                    <h1 className="text-3xl font-bold text-blue-700 mb-4">Projects</h1>
                    {loading && <div className="text-gray-500">Loading...</div>}
                    {error && <div className="text-red-500">{error}</div>}
                    <ul className="divide-y divide-gray-200">
                        {projects.map((project) => (
                            <li key={project.id} className="py-4 flex flex-col md:flex-row md:items-center md:justify-between">
                                <div>
                                    <Link href={`/project/${project.id}`} className="text-lg font-semibold text-blue-700 hover:underline">
                                        {project.name}
                                    </Link>
                                    <div className="text-sm text-gray-500">{project.location}</div>
                                    <div className="text-xs text-gray-400">Status: {project.status} | Elements: {project.element_count}</div>
                                </div>
                                <div className="mt-2 md:mt-0">
                                    <Link href={`/project/${project.id}`} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow transition">View</Link>
                                </div>
                            </li>
                        ))}
                    </ul>
                    <div className="mt-6">
                        <Link href="/project/new" className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow transition">+ New Project</Link>
                    </div>
                </div>
            </main>
        </>
    );
}
