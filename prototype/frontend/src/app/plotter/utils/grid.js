import transform from './domain_to_canvas.js';
import transform_c from './canvas_to_domain.js';
import { transform_x, transform_y } from './domain_to_canvas.js';
function roundTo(value, decimalCount) {
  const factor = Math.pow(10, decimalCount);
  return Math.round((value + Number.EPSILON) * factor) / factor;
}   
export default function grid_printer(ctx, x_dom, y_dom, canvas_domain, spacing_factor = 10){

    const x_domain = x_dom;
    const y_domain = y_dom;
    var cur = Math.floor(x_domain[0]) - (Math.floor(x_domain[0]) % spacing_factor);

    ctx.lineWidth = 1;
    ctx.strokeStyle = "black";

    while(cur < x_domain[1]){
        const x_canvas = transform_x(x_domain, canvas_domain, cur);

        if(cur == 0.0){
            ctx.lineWidth = 2;
        }
        ctx.font = '400 14px "Roboto", sans-serif';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        const test = transform(x_domain, y_domain, canvas_domain, cur, 0);
        ctx.fillText(roundTo(cur, 2), test[0] + 2, test[1] + 12);
        ctx.beginPath();
        ctx.moveTo(x_canvas, 0);
        ctx.lineTo(x_canvas, canvas_domain[1]);
        ctx.stroke();
        if(cur === 0){
            ctx.lineWidth = 1;
        }
        cur += spacing_factor;
    }
    cur = Math.floor(y_domain[0]) - (Math.floor(y_domain[0]) % spacing_factor);
    while(cur < y_domain[1]){
        const y_canvas = transform_y(y_domain, canvas_domain, cur);


        if(cur === 0){
            ctx.lineWidth = 2;
        }
        ctx.font = '400 14px "Roboto", sans-serif';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        if(roundTo(cur, 2) !== 0){
            const test = transform(x_domain, y_domain, canvas_domain, 0, cur);
            ctx.fillText(roundTo(cur, 5), test[0] + 5, test[1] - 4);
        }
        ctx.beginPath();
        ctx.moveTo(0, y_canvas);
        ctx.lineTo(canvas_domain[0], y_canvas);
        ctx.stroke();

        if(cur === 0){
            ctx.lineWidth = 1;
        }
        cur += spacing_factor;
    }
}
