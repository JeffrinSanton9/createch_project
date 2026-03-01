"use client";
import { useEffect, useState } from "react";
import NavBar from "@/app/components/Navibar.jsx";

export default function EquipmentPage() {
    const [equipment, setEquipment] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch("http://localhost:8000/api/equipment/")
            .then((res) => res.json())
            .then(setEquipment)
            .catch(() => setError("Failed to load equipment"))
            .finally(() => setLoading(false));
    }, []);

    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl mt-10 text-gray-900">
                    <h1 className="text-3xl font-bold text-blue-700 mb-4 text-center">Equipment</h1>
                    <div className="mb-6 text-right">
                        <a href="/equipment/new" className="inline-block bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded shadow transition">+ Add Equipment</a>
                    </div>
                    {loading && <div className="text-gray-500">Loading...</div>}
                    {error && <div className="text-red-500">{error}</div>}
                    <ul className="divide-y divide-gray-200">
                        {equipment.map((eq) => (
                            <li key={eq.id} className="py-4 flex flex-col md:flex-row md:items-center md:justify-between">
                                <div>
                                    <div className="text-lg font-semibold text-blue-700">{eq.name}</div>
                                    <div className="text-sm text-gray-500">{eq.type}</div>
                                    <div className="text-xs text-gray-400">Status: {eq.status} | Qty: {eq.quantity}</div>
                                    {eq.description && <div className="text-xs text-gray-500 mt-1">{eq.description}</div>}
                                </div>
                                <div className="mt-2 md:mt-0 text-xs text-gray-400">Added: {eq.created_at ? new Date(eq.created_at).toLocaleString() : "-"}</div>
                            </li>
                        ))}
                    </ul>
                </div>
            </main>
        </>
    );
}
