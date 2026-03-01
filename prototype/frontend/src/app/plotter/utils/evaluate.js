import { compile, parse, evaluate } from 'mathjs'

export default function evaluator(x_domain, y_domain, canvas_domain, expr_com, x){
    
    const res = expr_com.evaluate({x});
    if(Math.abs(res) > 40000){
        return NaN;
    }
    return res;  
}

