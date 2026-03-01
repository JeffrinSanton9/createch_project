"use client";
import { useEffect, useState } from "react";
import NavBar from "@/app/components/Navibar.jsx";
import { getSignals, evaluateScenario, predictTime, predictCost } from "@/lib/simulationApi";

export default function SimulationPage() {
    const [signals, setSignals] = useState([]);
    const [form, setForm] = useState({});
    const [result, setResult] = useState(null);
    const [mode, setMode] = useState("evaluate"); // "evaluate", "predictTime", "predictCost"
    const [extra, setExtra] = useState(""); // budget or days
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        getSignals().then((data) => {
            setSignals(data.signals);
            // Set defaults
            const defaults = {};
            data.signals.forEach(sig => { defaults[sig.name] = sig.min; });
            setForm(defaults);
        });
    }, []);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.type === "number" ? Number(e.target.value) : e.target.value });
    };

    const handleExtra = (e) => setExtra(e.target.value);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            let res;
            if (mode === "evaluate") {
                res = await evaluateScenario(form);
            } else if (mode === "predictTime") {
                res = await predictTime({ ...form, budget: Number(extra) });
            } else if (mode === "predictCost") {
                res = await predictCost({ ...form, days: Number(extra) });
            }
            setResult(res);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <NavBar />
            <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
                <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl mt-10 text-gray-900">
                    <h1 className="text-3xl font-bold text-blue-700 mb-4 text-center">Precast Yard Simulation</h1>
                    <div className="mb-4 flex flex-col md:flex-row gap-2 justify-center">
                        <button onClick={() => setMode("evaluate")} className={`px-4 py-2 rounded ${mode === "evaluate" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Evaluate</button>
                        <button onClick={() => setMode("predictTime")} className={`px-4 py-2 rounded ${mode === "predictTime" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Predict Time (given Budget)</button>
                        <button onClick={() => setMode("predictCost")} className={`px-4 py-2 rounded ${mode === "predictCost" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Predict Cost (given Days)</button>
                    </div>
                    <form onSubmit={handleSubmit} className="space-y-4 text-left">
                        {signals.map(sig => (
                            <div key={sig.name}>
                                <label className="block font-semibold mb-1">{sig.name.replace(/_/g, ' ')}
                                    <span className="text-xs text-gray-400 ml-2">({sig.description})</span>
                                </label>
                                <input
                                    name={sig.name}
                                    type={sig.type === "int" ? "number" : "number"}
                                    min={sig.min}
                                    max={sig.max}
                                    step={sig.type === "int" ? 1 : 0.01}
                                    value={form[sig.name] ?? sig.min}
                                    onChange={handleChange}
                                    className="w-full border rounded px-3 py-2"
                                />
                            </div>
                        ))}
                        {mode === "predictTime" && (
                            <div>
                                <label className="block font-semibold mb-1">Budget (₹ INR)</label>
                                <input type="number" min={1} value={extra} onChange={handleExtra} className="w-full border rounded px-3 py-2" required />
                            </div>
                        )}
                        {mode === "predictCost" && (
                            <div>
                                <label className="block font-semibold mb-1">Target Days</label>
                                <input type="number" min={1} value={extra} onChange={handleExtra} className="w-full border rounded px-3 py-2" required />
                            </div>
                        )}
                        {error && <div className="text-red-500 text-center">{error}</div>}
                        <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition">
                            {loading ? "Simulating..." : "Simulate"}
                        </button>
                    </form>
                    {result && (
                        <div className="mt-8">
                            {mode === "evaluate" && result.results && (
                                <>
                                    <h2 className="text-xl font-bold text-blue-600 mb-2">Results (All Curing Methods)</h2>
                                    <table className="w-full text-sm border">
                                        <thead>
                                            <tr className="bg-gray-100">
                                                <th className="p-2">Curing Method</th>
                                                <th className="p-2">Predicted Days</th>
                                                <th className="p-2">Predicted Cost</th>
                                                <th className="p-2">Groundtruth Days</th>
                                                <th className="p-2">Groundtruth Cost</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {result.results.map(r => (
                                                <tr key={r.curing_method}>
                                                    <td className="p-2 font-semibold">{r.curing_method}</td>
                                                    <td className="p-2">{r.predicted_days}</td>
                                                    <td className="p-2">₹{r.predicted_cost.toLocaleString()}</td>
                                                    <td className="p-2">{r.groundtruth_days}</td>
                                                    <td className="p-2">₹{r.groundtruth_cost.toLocaleString()}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            )}
                            {mode === "predictTime" && result.results && (
                                <>
                                    <h2 className="text-xl font-bold text-blue-600 mb-2">Predicted Days (Given Budget)</h2>
                                    <table className="w-full text-sm border">
                                        <thead>
                                            <tr className="bg-gray-100">
                                                <th className="p-2">Curing Method</th>
                                                <th className="p-2">Predicted Days</th>
                                                <th className="p-2">Predicted Cost</th>
                                                <th className="p-2">Recommended Complexity</th>
                                                <th className="p-2">Recommended Equip</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {result.results.map(r => (
                                                <tr key={r.curing_method}>
                                                    <td className="p-2 font-semibold">{r.curing_method}</td>
                                                    <td className="p-2">{r.predicted_days}</td>
                                                    <td className="p-2">₹{r.predicted_cost.toLocaleString()}</td>
                                                    <td className="p-2">{r.recommended_complexity}</td>
                                                    <td className="p-2">{(r.recommended_equip * 100).toFixed(0)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            )}
                            {mode === "predictCost" && result.results && (
                                <>
                                    <h2 className="text-xl font-bold text-blue-600 mb-2">Predicted Cost (Given Days)</h2>
                                    <table className="w-full text-sm border">
                                        <thead>
                                            <tr className="bg-gray-100">
                                                <th className="p-2">Curing Method</th>
                                                <th className="p-2">Predicted Days</th>
                                                <th className="p-2">Predicted Cost</th>
                                                <th className="p-2">Recommended Complexity</th>
                                                <th className="p-2">Recommended Equip</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {result.results.map(r => (
                                                <tr key={r.curing_method}>
                                                    <td className="p-2 font-semibold">{r.curing_method}</td>
                                                    <td className="p-2">{r.predicted_days}</td>
                                                    <td className="p-2">₹{r.predicted_cost.toLocaleString()}</td>
                                                    <td className="p-2">{r.recommended_complexity}</td>
                                                    <td className="p-2">{(r.recommended_equip * 100).toFixed(0)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
