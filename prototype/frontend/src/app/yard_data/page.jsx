"use client";
import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import NavBar from "@/app/components/Navibar.jsx";

const PlotCanvas = dynamic(() => import("@/app/plotter/PlotCanvas"), { ssr: false });

export default function YardDataAnalyzer() {
    const [data, setData] = useState([]); // {time, temperature, humidity}
    const [mode, setMode] = useState("temperature"); // "temperature" or "humidity"
    const socketRef = useRef(null);
    const [connected, setConnected] = useState(false);
    const [approxFn, setApproxFn] = useState("");
    const [approxLoading, setApproxLoading] = useState(false);
    const [approxError, setApproxError] = useState(null);

    useEffect(() => {
        socketRef.current = new WebSocket("ws://10.255.83.187:81");
        socketRef.current.onopen = () => {
            setConnected(true);
            socketRef.current.send("Hello ESP8266");
        };
        socketRef.current.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                // Expecting { time, temperature, humidity } or similar
                setData((prev) => [
                    ...prev,
                    {
                        time: msg.time ?? prev.length,
                        temperature: msg.temperature ?? msg.temp ?? 0,
                        humidity: msg.humidity ?? 0,
                        point_id: prev.length
                    }
                ]);
            } catch {
                // Ignore non-JSON
            }
        };
        socketRef.current.onerror = (error) => { setConnected(false); };
        socketRef.current.onclose = () => { setConnected(false); };
        return () => { socketRef.current.close(); };
    }, []);

    // Prepare data for plotter
    const dp = data.map((d) => ({
        x_value: d.time,
        y_value: mode === "temperature" ? d.temperature : d.humidity,
        point_id: d.point_id
    }));

    // Prepare points for backend approximation
    const points = dp.map((d) => [d.x_value, d.y_value]);

    const handleApproximate = async () => {
        setApproxLoading(true);
        setApproxError(null);
        setApproxFn("");
        try {
            const res = await fetch("http://localhost:8000/api/approximation/fit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ points, method: "polynomial" })
            });
            if (!res.ok) throw new Error("Failed to approximate");
            const { function: fn } = await res.json();
            setApproxFn(fn);
        } catch (err) {
            setApproxError("Failed to approximate: " + err.message);
        } finally {
            setApproxLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
            <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl mt-10 text-gray-900">
				<NavBar />
                <h2 className="text-2xl font-bold mb-4 text-blue-700 text-center">Yard Data Analyzer</h2>
                <div className="flex gap-4 mb-6 justify-center">
                    <button onClick={() => setMode("temperature")}
                        className={`px-4 py-2 rounded ${mode === "temperature" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Time vs Temperature</button>
                    <button onClick={() => setMode("humidity")}
                        className={`px-4 py-2 rounded ${mode === "humidity" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Time vs Humidity</button>
                </div>
                <PlotCanvas
                    expression={approxFn}
                    dp={dp}
                />
                <div className="mt-4 flex flex-col items-center gap-2">
                    <button onClick={handleApproximate} disabled={approxLoading || dp.length < 2}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded transition disabled:opacity-50">
                        {approxLoading ? "Approximating..." : "Approximate"}
                    </button>
                    {approxError && <div className="text-red-500 text-xs">{approxError}</div>}
                    {approxFn && <div className="text-xs text-green-700">Approximation: <span className="font-mono">{approxFn}</span></div>}
                </div>
                <div className="mt-4 text-center text-xs text-gray-500">
                    WebSocket: {connected ? "Connected" : "Disconnected"}
                </div>
            </div>
        </div>
    );
}
