import transform from "@/app/plotter/utils/domain_to_canvas.js";
export default function points_printer(x_domain, y_domain, canvas_domain, datapoints, ctx){
	for(let i = 0; i < datapoints.length; i++){
		const point = datapoints[i];
		const canvas_point = transform(x_domain, y_domain, canvas_domain, point.x_value, point.y_value);
		ctx.fillStyle = "blue";
		ctx.beginPath();
		ctx.arc(canvas_point[0], canvas_point[1], 4, 0, 2 * Math.PI);
		ctx.fill();
	}
}
