import evaluator from './evaluate.js';
import transform from './domain_to_canvas.js';
import { transform_x, transform_y } from './canvas_to_domain.js';

export default function plot_printer(ctx, x_dom, y_dom, canvas_domain, expression){
    var pre = undefined;
    const x_domain = x_dom;
    const y_domain = y_dom;
    const canvas_sampling_delta = 0.5;
    const domain_sampling_delta = canvas_sampling_delta * 10 * ((x_dom[1] - x_dom[0])/canvas_domain[0]);
    for(let x = x_domain[0]; x < x_domain[1]; x += 0.01){
        const y = evaluator(x_domain, y_domain, canvas_domain, expression, x);
        const canvas_point = transform(x_domain, y_domain, canvas_domain, x, y);

        if(pre === undefined){
            pre = canvas_point;
            continue;
        }

        ctx.lineWidth = 2;
        ctx.strokeStyle = "red";

        ctx.beginPath();
        ctx.moveTo(pre[0], pre[1]); 
        ctx.lineTo(canvas_point[0], canvas_point[1]); 
        ctx.stroke();
        
        pre = canvas_point;
    }
}
 
