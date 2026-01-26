import React, { useRef, useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

const GraphCanvas = ({ data, onNodeClick }) => {
  const graphRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // 1. AUTO-RESIZE LOGIC (Fixes the "Unclickable" bug)
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height
        });
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // Color Logic
  const getNodeColor = (node) => {
    const text = (node.department || node.group || node.name || "").toLowerCase();
    if (text.includes('computer') || text.includes('cs') || text.includes('tech')) return '#3b82f6';
    if (text.includes('health') || text.includes('med')) return '#ef4444';
    if (text.includes('business') || text.includes('econ')) return '#f59e0b';
    if (text.includes('env') || text.includes('sci')) return '#10b981';
    if (text.includes('project')) return '#f97316';
    return '#64748b';
  };

  return (
    <div ref={containerRef} className="w-full h-full bg-[#25aae1] cursor-pointer relative">
      <ForceGraph2D
        ref={graphRef}
        width={dimensions.width}   // <--- FORCE WIDTH
        height={dimensions.height} // <--- FORCE HEIGHT
        graphData={data}
        backgroundColor="#363d3f"  // Match the container blue
        linkColor={() => "rgba(255,255,255,0.2)"} // White links for blue bg
        linkWidth={1.5}
        enableNodeDrag={false}
        
        // 2. VISUAL DRAWING
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const color = getNodeColor(node);

          // Glow
          ctx.shadowColor = color;
          ctx.shadowBlur = 15;
          ctx.beginPath();
          ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
          ctx.fillStyle = color;
          ctx.fill();
          ctx.shadowBlur = 0; 

          // Label
          if (globalScale > 1.5 || node.val > 20) {
             ctx.font = `${fontSize}px Sans-Serif`;
             ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
             ctx.textAlign = "center";
             ctx.textBaseline = "middle";
             ctx.fillText(label, node.x, node.y + 12);
          }
        }}

        // 3. HIT DETECTION AREA (Crucial for clicks)
        nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 14, 0, 2 * Math.PI, false); // Big clickable target
            ctx.fill();
        }}
        
        // 4. CLICK HANDLER
        onNodeClick={(node) => {
            console.log("CLICK DETECTED:", node.name); // Check console to verify
            
            // Zoom in
            graphRef.current.centerAt(node.x, node.y, 1000);
            graphRef.current.zoom(4, 2000);
            
            // Trigger App action
            if (onNodeClick) onNodeClick(node);
        }}
      />
    </div>
  );
};

export default GraphCanvas;