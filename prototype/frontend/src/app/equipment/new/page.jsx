"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/app/components/Navibar.jsx";

export default function NewEquipmentPage() {
    const router = useRouter();
    const [form, setForm] = useState({
        name: "",
        type: "",
        description: "",
        status: "available",
        quantity: 1
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const res = await fetch("http://localhost:8000/api/equipment/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ...form, quantity: Number(form.quantity) })
            });
            if (!res.ok) throw new Error("Failed to create equipment");
            router.push("/equipment");
        } catch (err) {
            setError("Failed to create equipment");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-xl mt-10 text-center text-gray-900">
                    <h1 className="text-3xl font-bold text-blue-700 mb-4">Add New Equipment</h1>
                    <form onSubmit={handleSubmit} className="space-y-4 text-left">
                        <div>
                            <label className="block font-semibold mb-1">Name<span className="text-red-500">*</span></label>
                            <input name="name" value={form.name} onChange={handleChange} required className="w-full border rounded px-3 py-2" />
                        </div>
                        <div>
                            <label className="block font-semibold mb-1">Type<span className="text-red-500">*</span></label>
                            <input name="type" value={form.type} onChange={handleChange} required className="w-full border rounded px-3 py-2" />
                        </div>
                        <div>
                            <label className="block font-semibold mb-1">Description</label>
                            <textarea name="description" value={form.description} onChange={handleChange} className="w-full border rounded px-3 py-2" />
                        </div>
                        <div>
                            <label className="block font-semibold mb-1">Status</label>
                            <select name="status" value={form.status} onChange={handleChange} className="w-full border rounded px-3 py-2">
                                <option value="available">Available</option>
                                <option value="in_use">In Use</option>
                                <option value="maintenance">Maintenance</option>
                            </select>
                        </div>
                        <div>
                            <label className="block font-semibold mb-1">Quantity</label>
                            <input name="quantity" type="number" min="1" value={form.quantity} onChange={handleChange} className="w-full border rounded px-3 py-2" />
                        </div>
                        {error && <div className="text-red-500 text-center">{error}</div>}
                        <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition">
                            {loading ? "Adding..." : "Add Equipment"}
                        </button>
                        <div className="text-center mt-2">
                            <a href="/equipment" className="text-blue-600 hover:underline">Back to Equipment</a>
                        </div>
                    </form>
                </div>
            </main>
        </>
    );
}
