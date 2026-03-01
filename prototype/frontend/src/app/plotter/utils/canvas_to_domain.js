//will transform the points in the canvas domain to the function domain
export default function transform(x_domain, y_domain, canvas_domain, x, y){

    const x_fdomain = transform_x(x_domain, canvas_domain, x);
    const y_fdomain = transform_y(y_domain, canvas_domain, y);

    return [x_fdomain, y_fdomain];
}

//will transform the points in the canvas's x domain to the function's x domain
export function transform_x(x_domain, canvas_domain, y){
    
    //the points are (x_domain[0], 0) and (x_domain[1], canvas_domain[0])
    //line equation is (x - x_domain[0])/(x_domain[1]-x_domain[0]) == (y)/(canvas_domain[0])
    const x_fdomain = ((y * (x_domain[1] - x_domain[0]))/(canvas_domain[0])) + x_domain[0];
    return x_fdomain;
}

//will transform the points in the canvas's y domain to the function's y domain
export function transform_y(y_domain, canvas_domain, x){

    //the points are (y_domain[0], 0) and (y_domain[1], canvas_domain[1])
    //line equation is (x - y_domain[0])/(y_domain[1] - y_domain[0]) == (y)/(canvas_domain[1])
    const y_fdomain = ((x * (y_domain[0] - y_domain[1]))/(canvas_domain[1])) + y_domain[1];
    return y_fdomain;
}
