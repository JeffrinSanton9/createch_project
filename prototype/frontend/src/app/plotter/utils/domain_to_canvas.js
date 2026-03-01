//will transform the points in the function domain to the canvas domain
export default function transform(x_domain, y_domain, canvas_domain, x, y){

    const x_canvas = transform_x(x_domain, canvas_domain, x);
    const y_canvas = transform_y(y_domain, canvas_domain, y);

    return [x_canvas, y_canvas];
}

//will transform the points in the function's x domain to the canvas's x domain
export function transform_x(x_domain, canvas_domain, y){

    //the points are (0, x_domain[0]) and (canvas_domain[0], x_domain[1])
    const x_canvas = ((canvas_domain[0] - 0)/(x_domain[1] - x_domain[0]) * (y - x_domain[0]));
 
    return x_canvas;
}

//will transform the points in the function's y domain to the canvas's y domain
export function transform_y(y_domain, canvas_domain, x){

    //the points are (0, y_domain[0]) and (canvas_domain[1], y_domain[1])
    const y_canvas = ((canvas_domain[1] - 0)/(y_domain[0] - y_domain[1]) * (x - y_domain[1])); 

    return y_canvas;
}
