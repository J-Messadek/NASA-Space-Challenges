import React, { useState, useEffect, useRef } from 'react';
import { Network, Share2, Search, Users, Target, BookOpen, Tag, ChevronDown, ChevronUp } from 'lucide-react';
import { Network as VisNetwork } from 'vis-network';
import { DataSet } from 'vis-data';
import './GraphVisualization.css';

const GraphVisualization = () => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchSummary, setSearchSummary] = useState(null);
  const [graphStats, setGraphStats] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    statistics: true,
    centrality: false
  });

  const networkRef = useRef(null);
  const containerRef = useRef(null);

  // Load graph statistics on component mount
  useEffect(() => {
    loadGraphStatistics();
    loadGraphData();
  }, []);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSearchResults && !event.target.closest('.header-search')) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSearchResults]);

  // Initialize network when container is ready
  useEffect(() => {
    if (containerRef.current && graphData) {
      initializeNetwork();
    }
  }, [graphData]);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load actual graph data from the API - no fallback data
      const response = await fetch('http://localhost:5000/api/graph/export');
      if (response.ok) {
        const data = await response.json();
        
        // Convert the real graph data to vis-network format - show ALL nodes and edges
        const nodes = data.nodes.map(node => ({
          id: node.id,
          label: node.label.length > 25 ? node.label.substring(0, 25) + '...' : node.label,
          group: node.type,
          title: node.label,
          value: node.weight || 1
        }));
        
        const edges = data.edges.map(edge => ({
          from: edge.source,
          to: edge.target,
          width: 1,
          color: { color: '#97C2FC' }
        }));
        
        setGraphData({ nodes, edges });
        console.log(`Loaded complete graph: ${nodes.length} nodes, ${edges.length} edges`);
      } else {
        // If API fails, show empty graph with error message
        setGraphData({ nodes: [], edges: [] });
        setError('Failed to load graph data from server');
      }
    } catch (error) {
      console.error('Error loading graph data:', error);
      setGraphData({ nodes: [], edges: [] });
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };


  const loadAuthorNetwork = async (authorName) => {
    try {
      // Get the author's collaboration network from the backend
      const response = await fetch(`http://localhost:5000/api/graph/author/${encodeURIComponent(authorName)}/collaboration-network?depth=2`);
      if (response.ok) {
        const data = await response.json();
        const network = data.data;
        
        if (network && network.nodes && network.nodes.length > 0) {
          // Convert the network data to vis-network format
          const nodes = network.nodes.map(node => ({
            id: node.id,
            label: node.label.length > 20 ? node.label.substring(0, 20) + '...' : node.label,
            group: node.type,
            title: node.label,
            value: node.weight || 1
          }));
          
          const edges = network.edges.map(edge => ({
            from: edge.source,
            to: edge.target,
            width: 2,
            color: { color: '#4ECDC4' },
            dashes: true
          }));
          
          setGraphData({ nodes, edges });
          
          // Fit the network to show all nodes
          setTimeout(() => {
            if (networkRef.current) {
              networkRef.current.fit();
            }
          }, 100);
        } else {
          // If no collaboration network, show author's direct connections
          await loadAuthorDirectConnections(authorName);
        }
      } else {
        // Fallback to direct connections if collaboration network fails
        await loadAuthorDirectConnections(authorName);
      }
    } catch (error) {
      console.error('Error loading author network:', error);
      // Fallback to direct connections
      await loadAuthorDirectConnections(authorName);
    }
  };

  const loadAuthorDirectConnections = async (authorName) => {
    try {
      // Get the author's direct information
      const authorResponse = await fetch(`http://localhost:5000/api/graph/author/${encodeURIComponent(authorName)}`);
      if (authorResponse.ok) {
        const authorData = await authorResponse.json();
        const authorInfo = authorData.data;
        
        // Create a meaningful network showing the author's research context
        const nodes = [];
        const edges = [];
        
        // Add the main author
        nodes.push({
          id: `author_${authorName.replace(/\s+/g, '_').toLowerCase()}`,
          label: authorName,
          group: 'author',
          title: `${authorName} (${authorInfo.collaboration_count} collaborations, ${authorInfo.publication_count} publications)`,
          value: Math.max(authorInfo.collaboration_count, authorInfo.publication_count) + 5
        });
        
        // Add co-authors (limit to top 10 to avoid clutter)
        authorInfo.co_authors.slice(0, 10).forEach((coAuthor, index) => {
          const coAuthorId = `author_${coAuthor.replace(/\s+/g, '_').toLowerCase()}`;
          nodes.push({
            id: coAuthorId,
            label: coAuthor,
            group: 'author',
            title: coAuthor,
            value: 3
          });
          
          // Add edge between main author and co-author
          edges.push({
            from: `author_${authorName.replace(/\s+/g, '_').toLowerCase()}`,
            to: coAuthorId,
            width: 2,
            color: { color: '#4ECDC4' },
            dashes: true
          });
        });
        
        // Add publications (limit to top 5 to avoid clutter)
        authorInfo.publications.slice(0, 5).forEach((pub, index) => {
          const pubId = `pub_${index}`;
          nodes.push({
            id: pubId,
            label: pub.title.length > 25 ? pub.title.substring(0, 25) + '...' : pub.title,
            group: 'publication',
            title: pub.title,
            value: 2
          });
          
          // Add edge between author and publication
          edges.push({
            from: `author_${authorName.replace(/\s+/g, '_').toLowerCase()}`,
            to: pubId,
            width: 1,
            color: { color: '#FF6B6B' }
          });
        });
        
        setGraphData({ nodes, edges });
        
        // Fit the network to show all nodes
        setTimeout(() => {
          if (networkRef.current) {
            networkRef.current.fit();
          }
        }, 100);
      }
    } catch (error) {
      console.error('Error loading author direct connections:', error);
      setError('Failed to load author network');
    }
  };

  const initializeNetwork = () => {
    if (!containerRef.current || !graphData) return;

    const options = {
      nodes: {
        shape: 'dot',
        scaling: {
          min: 8,
          max: 25,
          label: {
            min: 6,
            max: 20,
            maxVisible: 50,
            drawThreshold: 8
          },
          customScalingFunction: (min, max, total, value) => {
            if (max === min) return 0.5;
            return (value - min) / (max - min);
          }
        },
        font: {
          size: 12,
          face: 'arial'
        },
        borderWidth: 2,
        shadow: true
      },
      edges: {
        width: 2,
        color: { inherit: 'from' },
        smooth: {
          type: 'continuous'
        }
      },
      groups: {
        author: {
          color: { background: '#4ECDC4', border: '#45B7D1' },
          font: { color: '#333' }
        },
        theme: {
          color: { background: '#96CEB4', border: '#7FB069' },
          font: { color: '#333' }
        },
        publication: {
          color: { background: '#FF6B6B', border: '#E74C3C' },
          font: { color: '#333' }
        },
        journal: {
          color: { background: '#45B7D1', border: '#3498DB' },
          font: { color: '#333' }
        },
        keyword: {
          color: { background: '#FFEAA7', border: '#FDCB6E' },
          font: { color: '#333' }
        }
      },
      physics: {
        enabled: true,
        stabilization: { iterations: 200 },
        barnesHut: {
          gravitationalConstant: -3000,
          centralGravity: 0.2,
          springLength: 120,
          springConstant: 0.03,
          damping: 0.12,
          avoidOverlap: 0.2
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        hideEdgesOnDrag: true
      }
    };

    const nodes = new DataSet(graphData.nodes);
    const edges = new DataSet(graphData.edges);
    
    const data = { nodes, edges };
    
    networkRef.current = new VisNetwork(containerRef.current, data, options);
    
    // Add event listeners
    networkRef.current.on('selectNode', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        handleNodeClick(nodeId);
      }
    });
    
    networkRef.current.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        handleNodeClick(nodeId);
        networkRef.current.selectNodes([nodeId]);
      } else {
        setSelectedNode(null);
        networkRef.current.unselectAll();
      }
    });
  };

  const loadGraphStatistics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/graph/statistics');
      if (response.ok) {
        const data = await response.json();
        setGraphStats(data.data);
      }
    } catch (error) {
      console.error('Error loading graph statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      setShowSearchResults(false);
      setSearchSummary(null);
      return;
    }

    // Only search if query is at least 2 characters
    if (query.trim().length < 2) {
      setSearchResults([]);
      setShowSearchResults(false);
      setSearchSummary(null);
      return;
    }

    try {
      setIsSearching(true);
      const response = await fetch(`http://localhost:5000/api/graph/search?q=${encodeURIComponent(query)}&limit=10`);
      
      if (response.ok) {
        const data = await response.json();
        const results = data.data.results;
        setSearchResults(results);
        setShowSearchResults(true);
        
        // Create search summary
        const summary = createSearchSummary(query, results);
        setSearchSummary(summary);
      } else {
        console.error('Search failed with status:', response.status);
        setSearchResults([]);
        setShowSearchResults(false);
        setSearchSummary(null);
      }
    } catch (error) {
      console.error('Error searching graph:', error);
      setSearchResults([]);
      setShowSearchResults(false);
      setSearchSummary(null);
    } finally {
      setIsSearching(false);
    }
  };

  const createSearchSummary = (query, results) => {
    if (!results || results.length === 0) {
      return {
        query,
        totalFound: 0,
        typeBreakdown: {},
        topResults: []
      };
    }

    // Count by type
    const typeBreakdown = results.reduce((acc, result) => {
      acc[result.type] = (acc[result.type] || 0) + 1;
      return acc;
    }, {});

    // Get top 3 results for preview
    const topResults = results.slice(0, 3).map(result => ({
      id: result.id,
      label: result.label,
      type: result.type,
      properties: result.properties
    }));

    return {
      query,
      totalFound: results.length,
      typeBreakdown,
      topResults,
      hasMore: results.length >= 10 // API limit is 10
    };
  };

  const handleSearchInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    handleSearch(query);
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter' && searchResults.length > 0) {
      // Select the first search result
      const firstResult = searchResults[0];
      handleNodeClick(firstResult.id);
      setShowSearchResults(false);
      setSearchQuery('');
      setSearchResults([]);
      
      // Focus on the selected node (only if it exists)
      if (networkRef.current) {
        const nodeExists = graphData && graphData.nodes.some(node => node.id === firstResult.id);
        if (nodeExists) {
          networkRef.current.focus(firstResult.id, {
            scale: 1.2,
            animation: {
              duration: 1000,
              easingFunction: "easeInOutQuad"
            }
          });
        } else {
          console.log(`Node ${firstResult.id} not found in current graph view`);
        }
      }
    } else if (e.key === 'Escape') {
      setShowSearchResults(false);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const handleNodeClick = async (nodeId) => {
    try {
      // Determine node type and fetch appropriate data
      const searchResponse = await fetch(`http://localhost:5000/api/graph/search?q=${encodeURIComponent(nodeId)}&limit=1`);
      if (searchResponse.ok) {
        const searchData = await searchResponse.json();
        if (searchData.data.results.length > 0) {
          const node = searchData.data.results[0];
          
          // If it's an author, fetch detailed author information
          if (node.type === 'author') {
            const authorResponse = await fetch(`http://localhost:5000/api/graph/author/${encodeURIComponent(node.label)}`);
            if (authorResponse.ok) {
              const authorData = await authorResponse.json();
              const authorInfo = authorData.data;
              
              // Enhance the node with detailed information
              const enhancedNode = {
                ...node,
                properties: {
                  ...node.properties,
                  publication_count: authorInfo.publication_count,
                  collaboration_count: authorInfo.collaboration_count,
                  co_authors: authorInfo.co_authors,
                  publications: authorInfo.publications
                }
              };
              
              setSelectedNode(enhancedNode);
              await loadAuthorNetwork(node.label);
              
              // Select and focus on the node in the network (only if it exists)
              if (networkRef.current) {
                const nodeExists = graphData && graphData.nodes.some(node => node.id === nodeId);
                if (nodeExists) {
                  networkRef.current.selectNodes([nodeId]);
                  setTimeout(() => {
                    networkRef.current.focus(nodeId, {
                      scale: 1.2,
                      animation: {
                        duration: 1000,
                        easingFunction: "easeInOutQuad"
                      }
                    });
                  }, 100);
                } else {
                  console.log(`Node ${nodeId} not found in current graph view`);
                }
              }
            } else {
              setSelectedNode(node);
              // Select and focus on the node in the network (only if it exists)
              if (networkRef.current) {
                const nodeExists = graphData && graphData.nodes.some(node => node.id === nodeId);
                if (nodeExists) {
                  networkRef.current.selectNodes([nodeId]);
                  setTimeout(() => {
                    networkRef.current.focus(nodeId, {
                      scale: 1.2,
                      animation: {
                        duration: 1000,
                        easingFunction: "easeInOutQuad"
                      }
                    });
                  }, 100);
                } else {
                  console.log(`Node ${nodeId} not found in current graph view`);
                }
              }
            }
          } else {
            setSelectedNode(node);
            // Select and focus on the node in the network
            if (networkRef.current) {
              networkRef.current.selectNodes([nodeId]);
              setTimeout(() => {
                networkRef.current.focus(nodeId, {
                  scale: 1.2,
                  animation: {
                    duration: 1000,
                    easingFunction: "easeInOutQuad"
                  }
                });
              }, 100);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error fetching node details:', error);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getNodeTypeIcon = (type) => {
    switch (type) {
      case 'publication': return <BookOpen size={16} />;
      case 'author': return <Users size={16} />;
      case 'journal': return <BookOpen size={16} />;
      case 'theme': return <Target size={16} />;
      case 'keyword': return <Tag size={16} />;
      default: return <Network size={16} />;
    }
  };

  const getNodeTypeColor = (type) => {
    switch (type) {
      case 'publication': return '#FF6B6B';
      case 'author': return '#4ECDC4';
      case 'journal': return '#45B7D1';
      case 'theme': return '#96CEB4';
      case 'keyword': return '#FFEAA7';
      default: return '#DDA0DD';
    }
  };

  if (loading) {
    return (
      <div className="graph-loading">
        <div className="loading-spinner"></div>
        <h3>Loading Knowledge Graph...</h3>
        <p>Preparing the NASA Space Biology research network</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="graph-error">
        <h3>Error Loading Graph</h3>
        <p>{error}</p>
        <button onClick={loadGraphStatistics} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="graph-visualization">
      <div className="graph-header">
        <h2>
          <Network size={24} />
          NASA Space Biology Knowledge Graph
        </h2>
        <div className="header-search">
          <div className="search-container">
            {isSearching ? (
              <div className="search-loading">⟳</div>
            ) : (
              <Search size={20} className="search-icon" />
            )}
            <input
              type="text"
              placeholder="Search authors, publications, themes, journals, keywords..."
              value={searchQuery}
              onChange={handleSearchInputChange}
              onKeyDown={handleSearchKeyDown}
              className="search-input"
            />
            {searchQuery && (
              <button 
                className="clear-search-btn"
                onClick={() => {
                  setSearchQuery('');
                  setSearchResults([]);
                  setShowSearchResults(false);
                  setSearchSummary(null);
                }}
              >
                ×
              </button>
            )}
          </div>
          
          {showSearchResults && (
            <div className="header-search-results">
              {searchResults.length > 0 ? (
                searchResults.slice(0, 5).map((result) => (
                <div 
                  key={result.id} 
                  className={`search-result-item ${selectedNode && selectedNode.id === result.id ? 'selected' : ''}`}
                  onClick={async () => {
                    await handleNodeClick(result.id);
                    setShowSearchResults(false);
                    setSearchQuery(''); // Clear the search input
                    setSearchResults([]); // Clear search results
                    // Focus on the selected node in the graph (only if it exists)
                    if (networkRef.current) {
                      // Check if the node exists in the current graph
                      const nodeExists = graphData && graphData.nodes.some(node => node.id === result.id);
                      if (nodeExists) {
                        networkRef.current.focus(result.id, {
                          scale: 1.2,
                          animation: {
                            duration: 1000,
                            easingFunction: "easeInOutQuad"
                          }
                        });
                      } else {
                        console.log(`Node ${result.id} not found in current graph view`);
                      }
                    }
                  }}
                >
                  <div className="result-icon">
                    {getNodeTypeIcon(result.type)}
                  </div>
                  <div className="result-content">
                    <div className="result-label">{result.label}</div>
                    <div className="result-type">{result.type}</div>
                  </div>
                </div>
                ))
              ) : (
                <div className="no-search-results">
                  No results found for "{searchQuery}"
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="graph-container">
        {/* Left Sidebar */}
        <div className="graph-sidebar">
          {/* Statistics Section */}
          <div className="sidebar-section">
            <div className="section-header" onClick={() => toggleSection('statistics')}>
              <h3>Graph Statistics</h3>
              {expandedSections.statistics ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
            {expandedSections.statistics && graphStats && (
              <div className="section-content">
                <div className="stat-item">
                  <span className="stat-label">Total Nodes:</span>
                  <span className="stat-value">{graphStats.total_nodes}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Edges:</span>
                  <span className="stat-value">{graphStats.total_edges}</span>
                </div>
                
                <div className="stat-breakdown">
                  <h4>Node Types:</h4>
                  {Object.entries(graphStats.node_types).map(([type, count]) => (
                    <div key={type} className="type-item">
                      <div 
                        className="type-color" 
                        style={{ backgroundColor: getNodeTypeColor(type) }}
                      ></div>
                      <span className="type-name">{type.replace('_', ' ').toUpperCase()}</span>
                      <span className="type-count">{count}</span>
                    </div>
                  ))}
                </div>

                <div className="stat-breakdown">
                  <h4>Top Authors:</h4>
                  {graphStats.most_connected_authors?.slice(0, 5).map(([authorId, connections]) => (
                    <div key={authorId} className="top-item">
                      <span className="item-name">{authorId.replace('author_', '').replace(/_/g, ' ')}</span>
                      <span className="item-value">{connections} connections</span>
                    </div>
                  ))}
                </div>

                <div className="stat-breakdown">
                  <h4>Top Themes:</h4>
                  {Object.entries(graphStats.theme_distribution || {}).slice(0, 5).map(([themeId, count]) => (
                    <div key={themeId} className="top-item">
                      <span className="item-name">{themeId.replace('theme_', '').replace(/_/g, ' ')}</span>
                      <span className="item-value">{count} papers</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>


        </div>

        {/* Main Graph Area */}
        <div className="graph-main">
          <div className="graph-canvas-container">
            {error ? (
              <div className="error-message">
                <h3>⚠️ Connection Error</h3>
                <p>{error}</p>
                <p>Make sure the backend API is running on port 5000</p>
                <button onClick={() => {
                  setError(null);
                  loadGraphData();
                }} className="retry-btn">
                  Retry
                </button>
              </div>
            ) : (
              <div ref={containerRef} className="graph-canvas" />
            )}
            
            
            <div className="graph-overlay">
              <div className="graph-controls">
                <button 
                  className="control-btn" 
                  title="Zoom In"
                  onClick={() => networkRef.current?.moveTo({ scale: 1.2 })}
                >
                  +
                </button>
                <button 
                  className="control-btn" 
                  title="Zoom Out"
                  onClick={() => networkRef.current?.moveTo({ scale: 0.8 })}
                >
                  -
                </button>
                <button 
                  className="control-btn" 
                  title="Reset View"
                  onClick={() => networkRef.current?.fit()}
                >
                  ⌂
                </button>
                <button 
                  className="control-btn" 
                  title="Back to Overview"
                  onClick={() => loadGraphData()}
                >
                  ↶
                </button>
                <button 
                  className="control-btn" 
                  title="Fullscreen"
                  onClick={() => {
                    if (document.fullscreenElement) {
                      document.exitFullscreen();
                    } else {
                      containerRef.current?.requestFullscreen();
                    }
                  }}
                >
                  ⛶
                </button>
              </div>
            </div>
          </div>
          
          <div className="graph-legend">
            <h4>Legend</h4>
            <div className="legend-items">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#FF6B6B' }}></div>
                <span>Publications</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#4ECDC4' }}></div>
                <span>Authors</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#45B7D1' }}></div>
                <span>Journals</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#96CEB4' }}></div>
                <span>Themes</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#FFEAA7' }}></div>
                <span>Keywords</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Node Details */}
        {selectedNode && (
          <div className="right-sidebar">
            <div className="node-details-card">
              <div className="card-header">
                <div className="node-icon">
                  {getNodeTypeIcon(selectedNode.type)}
                </div>
                <div className="node-title">
                  <h3>{selectedNode.label}</h3>
                  <span className="node-type">{selectedNode.type}</span>
                </div>
                <button 
                  className="close-btn"
                  onClick={() => setSelectedNode(null)}
                >
                  ×
                </button>
              </div>
              
              <div className="card-content">
                {selectedNode.type === 'author' && (
                  <div className="author-details">
                    <div className="detail-section">
                      <h4>Research Activity</h4>
                      <div className="stats-grid">
                        <div className="stat-item">
                          <span className="stat-label">Publications</span>
                          <span className="stat-value">{selectedNode.properties?.publication_count || 'N/A'}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Collaborations</span>
                          <span className="stat-value">{selectedNode.properties?.collaboration_count || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                    
                    {selectedNode.properties?.co_authors && selectedNode.properties.co_authors.length > 0 && (
                      <div className="detail-section">
                        <h4>Top Collaborators</h4>
                        <div className="collaborator-list">
                          {selectedNode.properties.co_authors.slice(0, 5).map((collaborator, index) => (
                            <div key={index} className="collaborator-item">
                              <span className="collaborator-name">{collaborator}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {selectedNode.properties?.publications && selectedNode.properties.publications.length > 0 && (
                      <div className="detail-section">
                        <h4>Recent Publications</h4>
                        <div className="publication-list">
                          {selectedNode.properties.publications.slice(0, 3).map((pub, index) => (
                            <div key={index} className="publication-item">
                              <span className="publication-title">{pub.title}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {selectedNode.type === 'publication' && (
                  <div className="publication-details">
                    <div className="detail-section">
                      <h4>Publication Details</h4>
                      <div className="publication-info">
                        <div className="info-item">
                          <span className="info-label">Title</span>
                          <span className="info-value">{selectedNode.label}</span>
                        </div>
                        {selectedNode.properties?.journal && (
                          <div className="info-item">
                            <span className="info-label">Journal</span>
                            <span className="info-value">{selectedNode.properties.journal}</span>
                          </div>
                        )}
                        {selectedNode.properties?.year && (
                          <div className="info-item">
                            <span className="info-label">Year</span>
                            <span className="info-value">{selectedNode.properties.year}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {selectedNode.type === 'theme' && (
                  <div className="theme-details">
                    <div className="detail-section">
                      <h4>Research Theme</h4>
                      <div className="theme-info">
                        <div className="info-item">
                          <span className="info-label">Theme</span>
                          <span className="info-value">{selectedNode.label}</span>
                        </div>
                        {selectedNode.properties?.publication_count && (
                          <div className="info-item">
                            <span className="info-label">Publications</span>
                            <span className="info-value">{selectedNode.properties.publication_count}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {selectedNode.type === 'journal' && (
                  <div className="journal-details">
                    <div className="detail-section">
                      <h4>Journal Information</h4>
                      <div className="journal-info">
                        <div className="info-item">
                          <span className="info-label">Journal</span>
                          <span className="info-value">{selectedNode.label}</span>
                        </div>
                        {selectedNode.properties?.publication_count && (
                          <div className="info-item">
                            <span className="info-label">Publications</span>
                            <span className="info-value">{selectedNode.properties.publication_count}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {selectedNode.type === 'keyword' && (
                  <div className="keyword-details">
                    <div className="detail-section">
                      <h4>Keyword Information</h4>
                      <div className="keyword-info">
                        <div className="info-item">
                          <span className="info-label">Keyword</span>
                          <span className="info-value">{selectedNode.label}</span>
                        </div>
                        {selectedNode.properties?.publication_count && (
                          <div className="info-item">
                            <span className="info-label">Publications</span>
                            <span className="info-value">{selectedNode.properties.publication_count}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Right Sidebar - Search Summary */}
        {searchSummary && searchSummary.totalFound > 0 && (
          <div className="right-sidebar">
            <div className="node-details-card">
              <div className="card-header">
                <div className="node-icon">
                  <Search size={18} />
                </div>
                <div className="node-title">
                  <h3>Search Results</h3>
                  <span className="node-type">Summary</span>
                </div>
                <button 
                  className="close-btn"
                  onClick={() => setSearchSummary(null)}
                >
                  ×
                </button>
              </div>
              
              <div className="card-content">
                <div className="detail-section">
                  <h4>Search Query</h4>
                  <div className="search-query-display">
                    <span className="query-text">"{searchSummary.query}"</span>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Results Overview</h4>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">Total Found</span>
                      <span className="stat-value">{searchSummary.totalFound}</span>
                    </div>
                    {searchSummary.hasMore && (
                      <div className="stat-item">
                        <span className="stat-label">Showing</span>
                        <span className="stat-value">Top 10</span>
                      </div>
                    )}
                  </div>
                </div>

                {Object.keys(searchSummary.typeBreakdown).length > 0 && (
                  <div className="detail-section">
                    <h4>Results by Type</h4>
                    <div className="type-breakdown">
                      {Object.entries(searchSummary.typeBreakdown).map(([type, count]) => (
                        <div key={type} className="type-item">
                          <div 
                            className="type-color" 
                            style={{ backgroundColor: getNodeTypeColor(type) }}
                          ></div>
                          <span className="type-name">{type.replace('_', ' ').toUpperCase()}</span>
                          <span className="type-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {searchSummary.topResults.length > 0 && (
                  <div className="detail-section">
                    <h4>Top Results</h4>
                    <div className="top-results-list">
                      {searchSummary.topResults.map((result, index) => (
                        <div key={result.id} className="result-preview-item">
                          <div className="result-preview-icon">
                            {getNodeTypeIcon(result.type)}
                          </div>
                          <div className="result-preview-content">
                            <div className="result-preview-label">{result.label}</div>
                            <div className="result-preview-type">{result.type}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphVisualization;
