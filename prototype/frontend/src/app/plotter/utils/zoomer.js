import transform from '@/app/plotter/utils/canvas_to_domain.js';

export function zoom(anchor, x_domain, y_domain, canvas_domain, scale) {
    console.log(anchor);
    const [ax, ay] = transform(
        x_domain,
        y_domain,
        canvas_domain,
        anchor[0],
        anchor[1]
    );
    console.log(ax, ay);
    const new_x = [
        ax + (x_domain[0] - ax) * scale,
        ax + (x_domain[1] - ax) * scale,
    ];

    const new_y = [
        ay + (y_domain[0] - ay) * scale,
        ay + (y_domain[1] - ay) * scale,
    ];
	

    return {
        x_dom: new_x,
        y_dom: new_y,
    };
}
/*
*/
