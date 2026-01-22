import React, { useRef, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";

const GraphCanvas = ({ data, onNodeClick }) => {
  const graphRef = useRef();

  // Color Logic Helper
  const getNodeColor = (node) => {
    const text = (node.department || node.group || node.name || "").toLowerCase();
    if (text.includes('computer') || text.includes('cs') || text.includes('tech')) return '#3b82f6'; // Blue
    if (text.includes('health') || text.includes('med')) return '#ef4444'; // Red
    if (text.includes('business') || text.includes('econ')) return '#f59e0b'; // Orange
    if (text.includes('env') || text.includes('sci')) return '#10b981'; // Green
    if (text.includes('project')) return '#f97316'; // Orange Project
    return '#64748b'; // Slate
  };

  useEffect(() => {
    if (graphRef.current) {
        // Physics tweaks for stability
        graphRef.current.d3Force('center').strength(0.4); 
        graphRef.current.d3Force('charge').strength(-150);
        graphRef.current.d3Force('link').distance(60);
    }
  }, []);

  return (
    <div className="w-full h-full bg-[#020617] cursor-pointer">
      <ForceGraph2D
        ref={graphRef}
        graphData={data}
        backgroundColor="#dad2d2"
        linkColor={() => "rgba(0, 0, 0, 0.15)"}
        linkWidth={1.5}
        enableNodeDrag={false} // <--- IMPORTANT: Disabling drag makes clicking 10x more reliable
        
        // 1. VISUAL DRAWING
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const color = getNodeColor(node);

          // Glow
          ctx.shadowColor = color;
          ctx.shadowBlur = 15;
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
          ctx.fillStyle = color;
          ctx.fill();
          ctx.shadowBlur = 0; 

          // Text Label
          if (globalScale > 1.8 || node.val > 20) {
             ctx.font = `${fontSize}px Sans-Serif`;
             ctx.fillStyle = "rgba(0, 0, 0, 0.9)";
             ctx.textAlign = "center";
             ctx.textBaseline = "middle";
             ctx.fillText(label, node.x, node.y + 10);
          }
        }}

        // 2. HIT DETECTION (THIS WAS MISSING)
        nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color; // This "color" is a special interaction ID provided by the library
            ctx.beginPath();
            ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false); // Radius 8 makes it easy to click
            ctx.fill();
        }}
        
        // 3. CLICK HANDLER
        onNodeClick={(node) => {
            // Zoom logic
            graphRef.current.centerAt(node.x, node.y, 1000);
            graphRef.current.zoom(5, 2000);
            
            // Pass event up
            if (onNodeClick) onNodeClick(node);
        }}
      />
    </div>
  );
};

export default GraphCanvas;