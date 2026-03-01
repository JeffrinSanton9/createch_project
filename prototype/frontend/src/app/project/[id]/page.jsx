"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import NavBar from "@/app/components/Navibar.jsx";

export default function ProjectDetailPage() {
    const params = useParams();
    const projectId = params.id;
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(`http://localhost:8000/api/projects/${projectId}`)
            .then((res) => res.json())
            .then(setProject)
            .catch(() => setError("Failed to load project details"))
            .finally(() => setLoading(false));
    }, [projectId]);

    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl mt-10 text-gray-900">
                    <h1 className="text-3xl font-bold text-blue-700 mb-4 text-center">Project Details</h1>
                    {loading && <div className="text-gray-500">Loading...</div>}
                    {error && <div className="text-red-500">{error}</div>}
                    {project && (
                        <div className="text-left">
                            <div className="mb-2"><span className="font-semibold">Name:</span> {project.name}</div>
                            <div className="mb-2"><span className="font-semibold">Location:</span> {project.location}</div>
                            <div className="mb-2"><span className="font-semibold">Status:</span> {project.status}</div>
                            <div className="mb-2"><span className="font-semibold">Supervisor:</span> {project.supervisor}</div>
                            <div className="mb-2"><span className="font-semibold">Start Date:</span> {project.start_date}</div>
                            <div className="mb-2"><span className="font-semibold">End Date:</span> {project.end_date}</div>
                            <div className="mb-4"><span className="font-semibold">Description:</span> {project.description}</div>
                            <h2 className="text-xl font-bold text-blue-600 mt-6 mb-2">Elements</h2>
                            <ul className="divide-y divide-gray-200">
                                {project.elements && project.elements.length > 0 ? project.elements.map((el) => (
                                    <li key={el.id} className="py-3">
                                        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                                            <div>
                                                <span className="font-semibold text-blue-700">{el.name}</span>
                                                <span className="ml-2 text-xs text-gray-500">({el.type})</span>
                                                <div className="text-xs text-gray-400">Curing: {el.curing_status} | Grade: {el.grade}</div>
                                            </div>
                                            <div className="mt-2 md:mt-0">
                                                {/* Add link to element details if needed */}
                                            </div>
                                        </div>
                                    </li>
                                )) : <li className="text-gray-500">No elements found.</li>}
                            </ul>
                        </div>
                    )}
                    <div className="mt-6">
                        <Link href="/project" className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded shadow transition">Back to Projects</Link>
                    </div>
                </div>
            </main>
        </>
    );
}
