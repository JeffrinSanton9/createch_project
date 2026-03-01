export default function pan(x_domain, y_domain, canvas_domain, dx, dy) {
    // Calculate the range of the domains
    const x_range = x_domain[1] - x_domain[0];
    const y_range = y_domain[1] - y_domain[0];
    
    // Calculate pixels per unit for proper scaling
    const x_factor = canvas_domain[0] / x_range;  // pixels per x unit
    const y_factor = canvas_domain[1] / y_range;  // pixels per y unit
    
    // Convert pixel movement to domain movement
    const dx_domain = dx / x_factor;
    const dy_domain = dy / y_factor;
    
    return {
        x_dom: [
            x_domain[0] - dx_domain,
            x_domain[1] - dx_domain
        ],
        y_dom: [
            y_domain[0] + dy_domain,  // + because canvas y is inverted
            y_domain[1] + dy_domain
        ]
    };
}
