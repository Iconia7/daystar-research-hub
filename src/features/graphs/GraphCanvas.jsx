import React, { useRef, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";

const GraphCanvas = ({ data, onNodeClick }) => {
  const graphRef = useRef();

  const getNodeColor = (node) => {
    const text = (node.department || node.group || node.name || "").toLowerCase();
    if (text.includes('computer') || text.includes('cs') || text.includes('tech')) return '#3b82f6';
    if (text.includes('health') || text.includes('med')) return '#ef4444';
    if (text.includes('business') || text.includes('econ')) return '#f59e0b';
    if (text.includes('env') || text.includes('sci')) return '#10b981';
    if (text.includes('project')) return '#f97316';
    return '#64748b';
  };

  useEffect(() => {
    if (graphRef.current) {
        // Physics: Pull nodes slightly tighter
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
        backgroundColor="#020617"
        linkColor={() => "rgba(255,255,255,0.15)"}
        linkWidth={1.5}
        
        // 1. DRAW THE VISUAL NODE
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const color = getNodeColor(node);

          // Glow effect
          ctx.shadowColor = color;
          ctx.shadowBlur = 15;
          
          // Draw Circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
          ctx.fillStyle = color;
          ctx.fill();
          ctx.shadowBlur = 0; 

          // Draw Label on Zoom
          if (globalScale > 1.8 || node.val > 20) {
             ctx.font = `${fontSize}px Sans-Serif`;
             ctx.fillStyle = "rgba(255,255,255,0.9)";
             ctx.textAlign = "center";
             ctx.textBaseline = "middle";
             ctx.fillText(label, node.x, node.y + 10);
          }
        }}

        // 2. [NEW] DRAW THE HIT AREA (Essential for clicks!)
        nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false); // Slightly larger radius makes clicking easier
            ctx.fill();
        }}
        
        // 3. HANDLE CLICK
        onNodeClick={(node) => {
            // Zoom to node
            graphRef.current.centerAt(node.x, node.y, 1000);
            graphRef.current.zoom(5, 2000);
            if (onNodeClick) onNodeClick(node);
        }}
      />
    </div>
  );
};

export default GraphCanvas;