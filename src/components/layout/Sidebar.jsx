import React from 'react';
import { X, User, Folder, Hash } from 'lucide-react';

const Sidebar = ({ node, onClose }) => {
  if (!node) return null;

  // Choose icon based on node type
  const getIcon = () => {
    if (node.group === 'person') return <User size={40} className="text-blue-500" />;
    if (node.group === 'project') return <Folder size={40} className="text-orange-500" />;
    return <Hash size={40} className="text-green-500" />;
  };

  return (
    <div style={{
      position: 'absolute', right: 0, top: 0, height: '100%', width: '350px',
      background: 'white', boxShadow: '-2px 0 10px rgba(0,0,0,0.1)', padding: '20px', zIndex: 10
    }}>
      <button onClick={onClose} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer' }}>
        <X />
      </button>
      
      <div style={{ marginTop: '40px' }}>
        {getIcon()}
        <h2 style={{ margin: '10px 0' }}>{node.name}</h2>
        <span style={{ 
          background: '#eee', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', textTransform: 'uppercase' 
        }}>
          {node.group}
        </span>

        <div style={{ marginTop: '20px' }}>
          <h3>Intelligence Profile</h3>
          {node.department && <p><strong>Dept:</strong> {node.department}</p>}
          {node.status && <p><strong>Status:</strong> {node.status}</p>}
          {node.sdg && <p><strong>Impact:</strong> {node.sdg}</p>}
          
          {/* Member B will eventually hook this up to real data logic */}
          <h4>Expertise / Tags:</h4>
          <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
            {node.expertise?.map(tag => (
              <span key={tag} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '10px', fontSize: '12px' }}>
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;