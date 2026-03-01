"use client"
import { useRef, useEffect } from "react";
import { useState } from "react";
import "@/app/globals.css";
import grid_printer from "@/app/plotter/utils/grid.js";
import plot_printer from "@/app/plotter/utils/plot_printer.js";
import { zoom } from "@/app/plotter/utils/zoomer.js";
import pan from "@/app/plotter/utils/panner.js";
import { parse } from 'mathjs'
import points_printer from "@/app/plotter/utils/points_printer.js";

export default function Canvas({ expression="", dp = []}){
    const WIDTH = 500;
    const HEIGHT = 500;
    const [xFreeze, setXFreeze] = useState(false);
    const [yFreeze, setYFreeze] = useState(false);
    const spacing_values = useRef([
        [0.01, -70],
        [0.02, -60],
        [0.05, -50],
        [0.1, -40],
        [0.2, -30],
        [0.5, -15],
        [1, -5],
        [2, 0],
        [5, 4],
        [10, 10],
        [20, 18],
        [50, 25],
        [100, 35],
        [200, 42],
        [500, 52],
        [1000, 60],
        [2000, 72],
        [5000, 82],
        [10000, 60]
    ]);
    
    const index = useRef(7);  
    const count = useRef(0);
    const expr = parse(expression); 
    const expr_com = expr.compile();

    const canvasRef = useRef(null);
    const x_domain = useRef([-10, 10]);
    const y_domain = useRef([-10, 10]);
    const canvas_domain = [WIDTH, HEIGHT];

    const startX = useRef(0);
    const startY = useRef(0);
    const isDragging = useRef(false);
    //Restricting the x and y domain 
    // Zooming
    useEffect(() => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        if (!canvas) return;
        
        const onWheel = (e) => {
            e.preventDefault();
            
            if (e.deltaY < 0) {
                // Zoom in
                if(!xFreeze || !yFreeze){
                    count.current -= 1;
                }
                if (index.current > 0 && count.current < spacing_values.current[index.current][1]) {
                    index.current -= 1;
                }
                const { x_dom, y_dom } = zoom(
                    [e.clientX - rect.x, e.clientY - rect.y], 
                    x_domain.current, 
                    y_domain.current, 
                    canvas_domain,
                    0.9
                );
                if(!xFreeze){
                    x_domain.current = x_dom;
                }
                if(!yFreeze){
                    y_domain.current = y_dom;
                }
            } else {
                if(!xFreeze || !yFreeze){
                    count.current += 1;
                }
                if (index.current < spacing_values.current.length - 1 && 
                    count.current >= spacing_values.current[index.current + 1][1]) {
                    index.current += 1;
                }
                
                const { x_dom, y_dom } = zoom(
                    [e.clientX - rect.x , e.clientY - rect.y], 
                    x_domain.current, 
                    y_domain.current, 
                    canvas_domain, 
                    1.1
                );

                if(!xFreeze){
                    x_domain.current = x_dom;
                }
                if(!yFreeze){
                    y_domain.current = y_dom;
                }
                if(x_domain.current[0] < -1000){
                    x_domain.current[0] = -1000;
                    setXFreeze(true);
                }
                else{
                    setXFreeze(false);
                }
                if(y_domain.current[0] < -1000){
                    y_domain.current[0] = -1000;
                    setYFreeze(true);
                }
                else{
                    setYFreeze(false);
                }
                if(x_domain.current[1] > 1000){
                    x_domain.current[1] = 1000;
                    setXFreeze(true);
                }
                else{
                    setXFreeze(false);
                }
                if(y_domain.current[1] > 1000){
                    y_domain.current[1] = 1000;
                    setYFreeze(true);
                }
                else{
                    setYFreeze(false);
                }
                    

            }
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, WIDTH, HEIGHT);
            grid_printer(ctx, x_domain.current, y_domain.current, canvas_domain, spacing_values.current[index.current][0]);
            plot_printer(ctx, x_domain.current, y_domain.current, canvas_domain, expr_com);
			points_printer(x_domain.current, y_domain.current, canvas_domain, dp, ctx);
        }
        
        canvas.addEventListener("wheel", onWheel, { passive: false });
        return () => canvas.removeEventListener("wheel", onWheel);
    }, [expr_com]);

    // Panning
    useEffect(() => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        if (!canvas) return;

        const onMouseDown = (e) => {
            isDragging.current = true;
            startX.current = e.clientX - rect.x;
            startY.current = e.clientY - rect.y;
        }

        const onMouseMove = (e) => {
            if (!isDragging.current) return;

            const dx = e.clientX - rect.x - startX.current;
            const dy = e.clientY - rect.y - startY.current;

            const { x_dom, y_dom } = pan(
                x_domain.current, 
                y_domain.current, 
                canvas_domain, 
                dx, 
                dy
            );

            x_domain.current = x_dom;
            y_domain.current = y_dom;

            startX.current = e.clientX - rect.x;
            startY.current = e.clientY - rect.y;

            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, WIDTH, HEIGHT);
            grid_printer(ctx, x_domain.current, y_domain.current, canvas_domain, spacing_values.current[index.current][0]);
            plot_printer(ctx, x_domain.current, y_domain.current, canvas_domain, expr_com);
			points_printer(x_domain.current, y_domain.current, canvas_domain, dp, ctx);
        };
        
        const onMouseUp = () => {
            isDragging.current = false;
        }

        canvas.addEventListener("mouseup", onMouseUp);
        canvas.addEventListener("mousemove", onMouseMove);
        canvas.addEventListener("mousedown", onMouseDown);

        return () => {
            canvas.removeEventListener("mouseup", onMouseUp);
            canvas.removeEventListener("mousemove", onMouseMove);
            canvas.removeEventListener("mousedown", onMouseDown);
        }
    }, [expr_com]);

    useEffect(() => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        if (!canvas) return;
        
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, WIDTH, HEIGHT);
        grid_printer(ctx, x_domain.current, y_domain.current, canvas_domain, spacing_values.current[index.current][0]);
        plot_printer(ctx, x_domain.current, y_domain.current, canvas_domain, expr_com);
		points_printer(x_domain.current, y_domain.current, canvas_domain, dp, ctx);

    }, [expr_com]);

    return (
        <div className="bg-white rounded-lg shadow-lg p-4 flex flex-col items-center border border-blue-200">
            <h2 className="text-lg font-mono text-blue-700 mb-2">Plot: <span className="font-bold">{expression}</span></h2>
            <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} className="border border-gray-300 rounded-lg" />
            {/* Optionally show datapoints */}
            {dp && dp.length > 0 && (
                <div className="mt-4 w-full">
                    <h3 className="text-md font-mono text-purple-700 mb-1">Data Points</h3>
                    <ul className="grid grid-cols-2 gap-2 text-xs">
                        {dp.map(point => (
                            <li key={point.point_id} className="bg-blue-50 rounded px-2 py-1 font-mono">x: {point.x_value}, y: {point.y_value}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
