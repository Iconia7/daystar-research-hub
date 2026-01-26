import React, { useState, useEffect, useMemo } from 'react';
import GraphCanvas from './features/graphs/GraphCanvas';
import { 
  Search, Share2, Sparkles, X, Briefcase, Globe, 
  Network, Users, FolderOpen, Lightbulb, ChevronDown, 
  Mail, ExternalLink
} from 'lucide-react';

/* --- SUB-COMPONENTS --- */

const ResearchersView = ({ data }) => (
  <div className="p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto h-full pb-20 animate-fade-in">
    {data.map(node => (
      <div key={node.id} className="p-5 bg-white border border-white/5 rounded-2xl hover:bg-slate-50 transition-all group shadow-sm">
         <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-slate-700 flex items-center justify-center font-bold text-slate-300 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                {node.name ? node.name.substring(0,2) : "??"}
            </div>
            <div>
                <h3 className="font-bold text-black text-sm">{node.name}</h3>
                <p className="text-xs text-slate-500">{node.department}</p>
            </div>
         </div>
         <div className="mt-4 flex gap-2">
            <button className="flex-1 py-2 rounded-lg bg-black text-white text-xs font-medium hover:bg-slate-800 transition-colors">Profile</button>
         </div>
      </div>
    ))}
  </div>
);

const ProjectsView = ({ data }) => (
    <div className="p-8 space-y-4 overflow-y-auto h-full pb-20 animate-fade-in">
      {data.map(node => (
        <div key={node.id} className="p-6 bg-white border border-white/5 rounded-2xl flex items-center justify-between hover:shadow-md transition-all shadow-sm">
           <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-lg bg-orange-100 flex items-center justify-center text-orange-600">
                  <FolderOpen size={24} />
              </div>
              <div>
                  <h3 className="font-bold text-lg text-black">{node.name}</h3>
                  <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700 border border-green-200">{node.status || "Active"}</span>
                      <span className="text-xs text-slate-500">Started 2024</span>
                  </div>
              </div>
           </div>
           <button className="p-3 hover:bg-slate-100 rounded-xl text-slate-400 hover:text-black"><ExternalLink size={20}/></button>
        </div>
      ))}
    </div>
);

const OpportunitiesView = ({ opportunities }) => (
    <div className="p-8 h-full overflow-y-auto pb-20 animate-fade-in">
        <div className="max-w-3xl mx-auto space-y-6">
            {opportunities.length === 0 ? (
                <div className="text-center text-white mt-10">No opportunities found yet. Run the 'enrich_profiles' script!</div>
            ) : (
                opportunities.map(op => (
                    <div key={op.id} className="p-1 rounded-2xl bg-gradient-to-r from-purple-600 to-blue-600 mb-6">
                        <div className="bg-white p-6 rounded-xl">
                            <div className="flex items-center gap-2 mb-4 text-purple-600">
                                <Sparkles size={20} />
                                <span className="font-bold tracking-widest text-sm">AI MATCH ({op.match_score}%)</span>
                            </div>
                            <h2 className="text-2xl font-bold mb-2 text-black">{op.topic}</h2>
                            <p className="text-slate-600 mb-6">{op.reason || `High potential for collaboration between ${op.r1_name} and ${op.r2_name} based on their research history.`}</p>
                            <div className="flex gap-3">
                                <span className="px-3 py-1 bg-slate-100 rounded-lg text-xs font-bold">{op.r1_name}</span>
                                <span className="px-3 py-1 bg-slate-100 rounded-lg text-xs font-bold">{op.r2_name}</span>
                            </div>
                        </div>
                    </div>
                ))
            )}
        </div>
    </div>
);

/* --- MAIN APP COMPONENT --- */

function App() {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [opportunities, setOpportunities] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeTab, setActiveTab] = useState('graph');

  // 1. FETCH GRAPH DATA & OPPORTUNITIES
  useEffect(() => {
    // Fetch Graph
    fetch('http://localhost:8000/api/graph/')
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error("Graph API Error:", err));

    // Fetch Opportunities
    fetch('http://localhost:8000/api/opportunities/')
      .then(res => res.json())
      .then(setOpportunities)
      .catch(err => console.error("Opp API Error:", err));
  }, []);

  // 2. CALCULATE LIVE STATS (The "Quick Stats" Sidebar)
  const stats = useMemo(() => {
    const researchers = data.nodes.filter(n => n.group === 'person');
    const projects = data.nodes.filter(n => n.group === 'project');
    
    // Sum up all publications from researcher stats
    const totalPapers = researchers.reduce((acc, curr) => acc + (curr.stats?.publications || 0), 0);
    
    return {
        researchers: researchers.length,
        projects: projects.length,
        papers: totalPapers,
        collabs: data.links.length
    };
  }, [data]);

  return (
    <div className="flex h-screen w-screen bg-[#25aae1] text-slate-100 overflow-hidden font-sans selection:bg-purple-500/30">
      
      {/* LEFT SIDEBAR (Dynamic Stats) */}
      <div className="w-72 flex-none border-r border-white/10 bg-[#25aae1] flex flex-col z-20 shadow-2xl">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-900/50">
              <Share2 className="text-white" size={20} />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight tracking-tight text-white">Daystar Research Hub</h1>
              <p className="text-[10px] text-white/80 font-medium tracking-widest">INTELLIGENCE GRAPH</p>
            </div>
          </div>
        </div>

        {/* Dynamic Quick Stats */}
        <div className="p-6">
          <div className="flex items-center gap-2 mb-4">
             <div className="h-4 w-1 bg-purple-500 rounded-full"></div>
             <h3 className="text-xs font-bold text-white uppercase tracking-widest">Quick Stats</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <DashboardCard label="Researchers" value={stats.researchers} />
            <DashboardCard label="Papers" value={stats.papers} color="text-emerald-600" />
            <DashboardCard label="Projects" value={stats.projects} color="text-amber-600" />
            <DashboardCard label="Collabs" value={stats.collabs} color="text-purple-600" />
          </div>
        </div>

        {/* Dynamic Opportunities List */}
        <div className="px-6 mt-2 flex-1 overflow-y-auto">
           <div className="flex items-center gap-2 mb-4">
             <div className="h-4 w-1 bg-blue-500 rounded-full"></div>
             <h3 className="text-xs font-bold text-white uppercase tracking-widest">Top Opportunities</h3>
           </div>
           <div className="space-y-3">
             {opportunities.slice(0, 3).map((op, i) => (
                 <SuggestionCard 
                    key={op.id}
                    initials1={op.r1_initials || "A"} 
                    initials2={op.r2_initials || "B"} 
                    names={`${op.r1_name.split(' ')[0]} & ${op.r2_name.split(' ')[0]}`} // Short names
                    topic={op.topic} 
                    score={`${op.match_score}%`} 
                 />
             ))}
             {opportunities.length === 0 && <p className="text-xs text-white/50">Loading opportunities...</p>}
           </div>
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col relative bg-[#25aae1]">
        
        {/* Top Navigation */}
        <div className="h-16 border-b border-white/10 bg-[#25aae1]/50 backdrop-blur-md flex items-center justify-between px-6 z-10">
           <div className="flex items-center bg-white/20 px-4 py-2 rounded-xl border border-white/10 w-96 text-sm focus-within:bg-white/30 transition-all duration-300">
              <Search size={16} className="mr-3 text-white" />
              <input type="text" placeholder="Search researchers, topics..." className="bg-transparent border-none outline-none w-full placeholder-white/70 text-white" />
           </div>
           <div className="flex gap-3">
              <FilterDropdown label="All Departments" />
              <FilterDropdown label="All SDGs" />
           </div>
        </div>

        {/* Tabs */}
        <div className="px-6 pt-4 pb-0 bg-white border-b border-slate-200">
            <div className="flex gap-6">
                <TabButton active={activeTab === 'graph'} onClick={() => setActiveTab('graph')} icon={<Network size={16}/>} label="Network Graph" />
                <TabButton active={activeTab === 'researchers'} onClick={() => setActiveTab('researchers')} icon={<Users size={16}/>} label="Researchers" />
                <TabButton active={activeTab === 'projects'} onClick={() => setActiveTab('projects')} icon={<FolderOpen size={16}/>} label="Projects" />
                <TabButton active={activeTab === 'opportunities'} onClick={() => setActiveTab('opportunities')} icon={<Lightbulb size={16}/>} label="Opportunities" />
            </div>
        </div>

        {/* Content Views */}
        <div className="flex-1 relative overflow-hidden">
           
           {activeTab === 'graph' && (
              <>
                <GraphCanvas data={data} onNodeClick={setSelectedNode} />
                
                <div className="absolute top-6 left-6 pointer-events-none z-10">
                   <div className="bg-white/95 backdrop-blur border border-slate-200 p-5 rounded-2xl shadow-xl max-w-xs pointer-events-auto">
                       <h4 className="text-sm font-bold text-black mb-2">Interactive Network</h4>
                       <ul className="text-xs text-slate-500 space-y-2">
                           <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span> Click nodes to view details</li>
                           <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Drag nodes to rearrange</li>
                       </ul>
                   </div>
                </div>

                <div className="absolute bottom-6 left-6 pointer-events-none z-10">
                   <div className="bg-white/95 backdrop-blur border border-slate-200 p-4 rounded-xl shadow-xl pointer-events-auto">
                       <h4 className="text-[10px] font-bold text-black uppercase tracking-widest mb-3">Departments</h4>
                       <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                          <LegendItem color="#3b82f6" label="Computer Science" />
                          <LegendItem color="#ef4444" label="Public Health" />
                          <LegendItem color="#10b981" label="Env. Science" />
                          <LegendItem color="#f59e0b" label="Business" />
                       </div>
                   </div>
                </div>
              </>
           )}

           {activeTab === 'researchers' && <ResearchersView data={data.nodes.filter(n => n.group !== 'project')} />}
           {activeTab === 'projects' && <ProjectsView data={data.nodes.filter(n => n.group === 'project')} />}
           {activeTab === 'opportunities' && <OpportunitiesView opportunities={opportunities} />}
        </div>
      </div>

      {/* RIGHT SIDEBAR (Node Details) */}
      {selectedNode && (
        <div className="w-96 border-l border-white/10 bg-[#0f1014] flex flex-col shadow-2xl animate-slide-in-right z-30 absolute top-0 bottom-0 right-0">
           <div className="p-6 pb-0 flex justify-end">
              <button onClick={() => setSelectedNode(null)} className="p-2 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition-colors"><X size={20}/></button>
           </div>
           
           <div className="px-8 pb-8 flex flex-col items-center text-center border-b border-white/10">
                <div className="h-24 w-24 rounded-3xl bg-gradient-to-br from-[#84cc16] to-[#4d7c0f] flex items-center justify-center text-3xl font-bold text-white shadow-2xl shadow-lime-900/50 mb-4">
                    {selectedNode.name ? selectedNode.name.substring(0,2).toUpperCase() : "??"}
                </div>
                <h2 className="font-bold text-xl text-white mb-1">{selectedNode.name}</h2>
                <p className="text-slate-400 text-sm font-medium">{selectedNode.department || "Research Partner"}</p>
           </div>

           <div className="p-6 space-y-8 overflow-y-auto flex-1">
              {/* Using Real Stats from Backend */}
              <div className="grid grid-cols-3 gap-3">
                 <DetailStatBox label="Publications" value={selectedNode.stats?.publications || 0} color="text-emerald-400" />
                 <DetailStatBox label="h-index" value={selectedNode.stats?.hIndex || 0} color="text-amber-400" />
                 <DetailStatBox label="Citations" value={selectedNode.stats?.citations || 0} color="text-blue-400" />
              </div>

              <div>
                 <div className="flex items-center gap-2 mb-3 text-slate-400">
                    <Briefcase size={16} />
                    <span className="text-xs font-bold uppercase tracking-wider">Expertise Areas</span>
                 </div>
                 <div className="flex flex-wrap gap-2">
                    {selectedNode.tags && selectedNode.tags.length > 0 ? selectedNode.tags.map(tag => (
                       <span key={tag} className="px-3 py-1.5 bg-[#1e1b4b] border border-indigo-500/30 rounded-lg text-xs font-medium text-indigo-300">
                          {tag}
                       </span>
                    )) : <span className="text-xs text-slate-600">No tags available</span>}
                 </div>
              </div>

              <div>
                 <div className="flex items-center gap-2 mb-3 text-slate-400">
                    <Globe size={16} />
                    <span className="text-xs font-bold uppercase tracking-wider">SDG Alignment</span>
                 </div>
                 <div className="flex flex-wrap gap-2">
                    {(selectedNode.sdgs || []).map(sdg => (
                       <div key={sdg} className={`h-8 px-3 rounded-lg flex items-center gap-2 text-xs font-bold text-white shadow-lg ${getSDGColor(sdg)}`}>
                          <span className="bg-white/20 px-1.5 py-0.5 rounded text-[10px]">{sdg}</span>
                          Goal {sdg}
                       </div>
                    ))}
                    {(!selectedNode.sdgs || selectedNode.sdgs.length === 0) && <span className="text-xs text-slate-600">No SDG data</span>}
                 </div>
              </div>
           </div>

           <div className="p-6 border-t border-white/10">
             <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium shadow-lg shadow-indigo-900/20">View Full Profile</button>
           </div>
        </div>
      )}
    </div>
  );
}

/* --- UTILITIES --- */
const TabButton = ({ active, onClick, icon, label }) => (
    <button onClick={onClick} className={`flex items-center gap-2 pb-4 text-sm font-medium border-b-2 transition-all ${active ? 'text-indigo-600 border-indigo-600' : 'text-slate-500 border-transparent hover:text-black hover:border-slate-300'}`}>
        {icon} {label}
    </button>
);
const FilterDropdown = ({ label }) => ( <button className="flex items-center gap-2 px-4 py-2 text-xs font-medium bg-white/20 border border-white/10 rounded-xl text-white hover:bg-white/30 transition-all">{label} <ChevronDown size={14} /></button> );
const DashboardCard = ({ label, value, color = "text-black" }) => ( <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100"><div className={`text-2xl font-bold ${color}`}>{value}</div><div className="text-[10px] text-slate-500 font-medium uppercase mt-1">{label}</div></div> );
const SuggestionCard = ({ initials1, initials2, names, topic, score }) => ( <div className="p-4 bg-white rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-all cursor-pointer group"><div className="flex items-center justify-between mb-3"><div className="flex -space-x-2"><div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold ring-2 ring-white text-white">{initials1}</div><div className="h-8 w-8 rounded-full bg-lime-500 flex items-center justify-center text-xs font-bold text-black ring-2 ring-white">{initials2}</div></div><Sparkles size={14} className="text-purple-500 group-hover:animate-pulse" /></div><p className="text-sm font-semibold text-black">{names}</p><p className="text-[11px] text-slate-500">{topic}</p><div className="mt-2 text-[10px] bg-purple-100 text-purple-700 inline-block px-2 py-1 rounded border border-purple-200">{score} Match</div></div> );
const DetailStatBox = ({ label, value, color }) => ( <div className="bg-[#1e293b]/50 p-3 rounded-xl text-center border border-white/10"><div className={`text-xl font-bold ${color}`}>{value}</div><div className="text-[10px] text-slate-500 font-medium">{label}</div></div> );
const LegendItem = ({ color, label }) => ( <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full" style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}></div><span className="text-xs text-slate-500">{label}</span></div> );
const getSDGColor = (id) => ({ 1: 'bg-red-500', 2: 'bg-amber-500', 4: 'bg-red-600', 8: 'bg-red-800', 9: 'bg-orange-600' }[id] || 'bg-blue-600');

export default App;