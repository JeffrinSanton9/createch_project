"use client";
import Link from "next/link";
import NavBar from "@/app/components/Navibar.jsx";
export default function Home() {
    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-xl mt-20 text-center">
                    <h1 className="text-4xl font-bold text-blue-700 mb-4">Precast Yard Projects Handler</h1>
                    <p className="text-gray-600 mb-8">Manage your precast yard projects, equipment, and optimize workflows.</p>
                    <div className="flex flex-col gap-4">
                        <Link href="/project" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded shadow transition">View Projects</Link>
                        <Link href="/equipment" className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded shadow transition">View Equipment</Link>
                    </div>
                </div>
            </main>
        </>
    );
}
