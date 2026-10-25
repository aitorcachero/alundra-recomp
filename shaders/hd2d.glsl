// HD-2D Master Shader with Dynamic Ambient Side Extension (16:9 Trick)
// Eliminates 2D tile pop-in chunks while filling the 16:9 screen with real-time ambient lighting.

vec3 sampleColor(vec2 uv) {
    return texture(u_tex, clamp(uv, vec2(0.0), vec2(1.0))).rgb;
}

void main() {
    vec2 uv = v_uv;
    vec3 col;
    
    // In native 16:9, the pristine 4:3 game area is centered at [0.1244, 0.8756]
    // The lateral strips [0.0, 0.1244) and (0.8756, 1.0] are the reveal zones.
    const float leftEdge = 0.1244;
    const float rightEdge = 0.8756;
    
    if (uv.x >= leftEdge && uv.x <= rightEdge) {
        // --- 1. GAMEPLAY ZONE: 100% Crisp, Pixel-Perfect, Zero Glitches ---
        col = sampleColor(uv);
        
        // Edge detail clarification (micro-contrast for 4K / xBR)
        vec3 up    = sampleColor(uv + vec2(0.0, -u_rcp.y));
        vec3 down  = sampleColor(uv + vec2(0.0,  u_rcp.y));
        vec3 left  = sampleColor(uv + vec2(-u_rcp.x, 0.0));
        vec3 right = sampleColor(uv + vec2( u_rcp.x, 0.0));
        vec3 edge  = 4.0 * col - (up + down + left + right);
        col = clamp(col + 0.12 * edge, 0.0, 1.0);
        
        // Color grading & contrast
        col = (col - 0.5) * 1.06 + 0.5;
        
        // Subtle border transition shadow at the seam
        float distToBorder = min(uv.x - leftEdge, rightEdge - uv.x);
        float borderShadow = smoothstep(0.0, 0.012, distToBorder);
        col *= mix(0.88, 1.0, borderShadow);
    } else {
        // --- 2. LATERAL ZONE: Dynamic Ambient Glow (Always Visible, Zero Pop-in) ---
        // Instead of showing glitchy popping chunks, extend the valid edge color outwards
        float edgeX = (uv.x < leftEdge) ? (leftEdge + 0.005) : (rightEdge - 0.005);
        
        // Multi-tap vertical blur for soft atmospheric ambient room lighting
        vec3 ambient = vec3(0.0);
        float totalW = 0.0;
        for (int dy = -4; dy <= 4; dy++) {
            float w = exp(-float(dy * dy) / 8.0);
            ambient += sampleColor(vec2(edgeX, uv.y + float(dy) * u_rcp.y * 3.5)) * w;
            totalW += w;
        }
        ambient /= totalW;
        
        // Soft vignette falloff towards the monitor's outer bezel
        float distFromScreenEdge = (uv.x < leftEdge) ? (uv.x / leftEdge) : ((1.0 - uv.x) / (1.0 - rightEdge));
        float fade = smoothstep(0.0, 1.0, distFromScreenEdge);
        
        // Ambient color tone with warm diffuse lighting
        col = ambient * mix(0.42, 0.78, fade);
        col = (col - 0.5) * 1.05 + 0.5;
    }
    
    // Selective Vibrance Enhancement across the whole presentation
    float luma = dot(col, vec3(0.299, 0.587, 0.114));
    float maxCol = max(max(col.r, col.g), col.b);
    float minCol = min(min(col.r, col.g), col.b);
    float sat = maxCol - minCol;
    col = mix(vec3(luma), col, 1.0 + 0.20 * (1.0 - sat));
    
    o = vec4(clamp(col, 0.0, 1.0), 1.0);
}
