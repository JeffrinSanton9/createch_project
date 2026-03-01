import { parse, evaluate, compile } from 'mathjs'
//The func and its derivative should be parse and compiled before calling this function
export function newton_raphson(func, derivative, x_values, tolerance = 1e-09){
    const roots = new Set()
    for(let i = 0; i<x_values.length; i++){
        let guess = x_values[i];

        while(Math.abs(func.evaluate({ x : guess })) > tolerance){
           guess -= func.evaluate({ x : guess }) / derivative.evaluate({ x : guess });
        }
        roots.add(guess);
    }
    return roots;
}

