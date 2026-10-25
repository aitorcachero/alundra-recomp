// HD-2D Crystal-Clear Full-Screen Shader for Alundra
// 100% Full-Screen coverage with zero black borders, detail sharpening and rich vibrance.

vec3 sampleColor(vec2 uv) {
    return texture(u_tex, clamp(uv, vec2(0.0), vec2(1.0))).rgb;
}

void main() {
    vec2 uv = v_uv;
    vec3 c = sampleColor(uv);

    // Subtle edge detail clarification (makes 4K pixel-art and textures razor-sharp across the entire screen)
    vec3 up    = sampleColor(uv + vec2(0.0, -u_rcp.y));
    vec3 down  = sampleColor(uv + vec2(0.0,  u_rcp.y));
    vec3 left  = sampleColor(uv + vec2(-u_rcp.x, 0.0));
    vec3 right = sampleColor(uv + vec2( u_rcp.x, 0.0));
    vec3 edge  = 4.0 * c - (up + down + left + right);
    c = clamp(c + 0.12 * edge, 0.0, 1.0);

    // Color Tone Curve & Mild Contrast Expansion
    c = (c - 0.5) * 1.06 + 0.5;
    c = clamp(c, 0.0, 1.0);

    // Selective Vibrance Enhancement
    float luma = dot(c, vec3(0.299, 0.587, 0.114));
    float maxCol = max(max(c.r, c.g), c.b);
    float minCol = min(min(c.r, c.g), c.b);
    float sat = maxCol - minCol;
    float vibrance = 0.22;
    c = mix(vec3(luma), c, 1.0 + vibrance * (1.0 - sat));

    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
