import React, { useState, useEffect } from 'react';
import { BarChart3, Users, Target, BookOpen, TrendingUp, Network } from 'lucide-react';
import './GraphAnalysis.css';

const GraphAnalysis = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState('overview');

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      
      // Load multiple analysis endpoints in parallel
      const [statsResponse, centralityResponse] = await Promise.all([
        fetch(`${apiUrl}/api/graph/statistics`),
        fetch(`${apiUrl}/api/graph/centrality`)
      ]);

      if (statsResponse.ok && centralityResponse.ok) {
        const [statsData, centralityData] = await Promise.all([
          statsResponse.json(),
          centralityResponse.json()
        ]);

        setAnalysisData({
          statistics: statsData.data,
          centrality: centralityData.data
        });
      } else {
        throw new Error('Failed to load analysis data');
      }
    } catch (error) {
      console.error('Error loading analysis data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };


  const getNodeTypeIcon = (type) => {
    switch (type) {
      case 'publication': return <BookOpen size={16} />;
      case 'author': return <Users size={16} />;
      case 'journal': return <BookOpen size={16} />;
      case 'theme': return <Target size={16} />;
      case 'keyword': return <Target size={16} />;
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
      <div className="analysis-loading">
        <div className="loading-spinner"></div>
        <h3>Loading Graph Analysis...</h3>
        <p>Analyzing the NASA Space Biology research network</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-error">
        <h3>Error Loading Analysis</h3>
        <p>{error}</p>
        <button onClick={loadAnalysisData} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="analysis-error">
        <h3>No Analysis Data Available</h3>
        <p>Please ensure the knowledge graph is properly loaded.</p>
      </div>
    );
  }

  const { statistics, centrality } = analysisData;

  return (
    <div className="graph-analysis">
      <div className="analysis-header">
        <h2>
          <BarChart3 size={24} />
          Knowledge Graph Analysis
        </h2>
        <p>Deep insights into the NASA Space Biology research network</p>
      </div>

      {/* Analysis Navigation */}
      <div className="analysis-nav">
        <button 
          className={`nav-btn ${selectedAnalysis === 'overview' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('overview')}
        >
          <TrendingUp size={16} />
          Overview
        </button>
        <button 
          className={`nav-btn ${selectedAnalysis === 'authors' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('authors')}
        >
          <Users size={16} />
          Authors
        </button>
        <button 
          className={`nav-btn ${selectedAnalysis === 'themes' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('themes')}
        >
          <Target size={16} />
          Themes
        </button>
        <button 
          className={`nav-btn ${selectedAnalysis === 'centrality' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('centrality')}
        >
          <Network size={16} />
          Centrality
        </button>
      </div>

      {/* Analysis Content */}
      <div className="analysis-content">
        {selectedAnalysis === 'overview' && (
          <OverviewAnalysis statistics={statistics} />
        )}
        
        {selectedAnalysis === 'authors' && (
          <AuthorsAnalysis statistics={statistics} />
        )}
        
        {selectedAnalysis === 'themes' && (
          <ThemesAnalysis statistics={statistics} />
        )}
        
        {selectedAnalysis === 'centrality' && (
          <CentralityAnalysis centrality={centrality} />
        )}
        
      </div>
    </div>
  );
};

// Overview Analysis Component
const OverviewAnalysis = ({ statistics }) => (
  <div className="analysis-section">
    <h3>Network Overview</h3>
    
    <div className="overview-grid">
      <div className="overview-card">
        <div className="card-header">
          <Network size={24} />
          <h4>Network Size</h4>
        </div>
        <div className="card-content">
          <div className="metric">
            <span className="metric-value">{statistics.total_nodes}</span>
            <span className="metric-label">Total Nodes</span>
          </div>
          <div className="metric">
            <span className="metric-value">{statistics.total_edges}</span>
            <span className="metric-label">Total Edges</span>
          </div>
        </div>
      </div>

      <div className="overview-card">
        <div className="card-header">
          <Users size={24} />
          <h4>Collaboration Network</h4>
        </div>
        <div className="card-content">
          <div className="metric">
            <span className="metric-value">{statistics.collaboration_network_stats?.total_authors || 0}</span>
            <span className="metric-label">Total Authors</span>
          </div>
          <div className="metric">
            <span className="metric-value">{statistics.collaboration_network_stats?.connected_components || 0}</span>
            <span className="metric-label">Connected Components</span>
          </div>
          <div className="metric">
            <span className="metric-value">{statistics.collaboration_network_stats?.largest_component_size || 0}</span>
            <span className="metric-label">Largest Component</span>
          </div>
        </div>
      </div>

      <div className="overview-card">
        <div className="card-header">
          <Target size={24} />
          <h4>Research Themes</h4>
        </div>
        <div className="card-content">
          <div className="metric">
            <span className="metric-value">{Object.keys(statistics.theme_distribution || {}).length}</span>
            <span className="metric-label">Unique Themes</span>
          </div>
          <div className="metric">
            <span className="metric-value">
              {Object.values(statistics.theme_distribution || {}).reduce((a, b) => a + b, 0)}
            </span>
            <span className="metric-label">Total Publications</span>
          </div>
        </div>
      </div>
    </div>

    <div className="node-types-breakdown">
      <h4>Node Type Distribution</h4>
      <div className="breakdown-grid">
        {Object.entries(statistics.node_types || {}).map(([type, count]) => (
          <div key={type} className="breakdown-item">
            <div className="breakdown-icon">
              {type === 'publication' && <BookOpen size={20} />}
              {type === 'author' && <Users size={20} />}
              {type === 'journal' && <BookOpen size={20} />}
              {type === 'theme' && <Target size={20} />}
              {type === 'keyword' && <Target size={20} />}
            </div>
            <div className="breakdown-content">
              <div className="breakdown-label">{type.replace('_', ' ').toUpperCase()}</div>
              <div className="breakdown-count">{count}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Authors Analysis Component
const AuthorsAnalysis = ({ statistics }) => (
  <div className="analysis-section">
    <h3>Author Collaboration Analysis</h3>
    
    <div className="authors-grid">
      <div className="authors-card">
        <h4>Most Connected Authors</h4>
        <div className="authors-list">
          {statistics.most_connected_authors?.slice(0, 10).map(([authorId, connections], index) => (
            <div key={authorId} className="author-item">
              <div className="author-rank">#{index + 1}</div>
              <div className="author-info">
                <div className="author-name">
                  {authorId.replace('author_', '').replace(/_/g, ' ')}
                </div>
                <div className="author-connections">{connections} connections</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="authors-card">
        <h4>Most Productive Journals</h4>
        <div className="authors-list">
          {statistics.most_productive_journals?.slice(0, 10).map(([journalId, count], index) => (
            <div key={journalId} className="author-item">
              <div className="author-rank">#{index + 1}</div>
              <div className="author-info">
                <div className="author-name">
                  {journalId.replace('journal_', '').replace(/_/g, ' ')}
                </div>
                <div className="author-connections">{count} publications</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// Themes Analysis Component
const ThemesAnalysis = ({ statistics }) => (
  <div className="analysis-section">
    <h3>Research Theme Analysis</h3>
    
    <div className="themes-grid">
      {Object.entries(statistics.theme_distribution || {}).slice(0, 12).map(([themeId, count]) => (
        <div key={themeId} className="theme-card">
          <div className="theme-header">
            <Target size={20} />
            <h4>{themeId.replace('theme_', '').replace(/_/g, ' ')}</h4>
          </div>
          <div className="theme-content">
            <div className="theme-count">{count}</div>
            <div className="theme-label">Publications</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Centrality Analysis Component
const CentralityAnalysis = ({ centrality }) => (
  <div className="analysis-section">
    <h3>Network Centrality Analysis</h3>
    
    <div className="centrality-grid">
      <div className="centrality-card">
        <h4>Degree Centrality</h4>
        <p>Nodes with the most direct connections</p>
        <div className="centrality-list">
          {centrality.degree_centrality?.slice(0, 10).map((item, index) => (
            <div key={item.id} className="centrality-item">
              <div className="centrality-rank">#{index + 1}</div>
              <div className="centrality-info">
                <div className="centrality-name">{item.label}</div>
                <div className="centrality-score">Score: {item.score}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="centrality-card">
        <h4>Betweenness Centrality</h4>
        <p>Nodes that act as bridges between different parts of the network</p>
        <div className="centrality-list">
          {centrality.betweenness_centrality?.slice(0, 10).map((item, index) => (
            <div key={item.id} className="centrality-item">
              <div className="centrality-rank">#{index + 1}</div>
              <div className="centrality-info">
                <div className="centrality-name">{item.label}</div>
                <div className="centrality-score">Score: {item.score}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="centrality-card">
        <h4>Closeness Centrality</h4>
        <p>Nodes that can reach other nodes with the fewest steps</p>
        <div className="centrality-list">
          {centrality.closeness_centrality?.slice(0, 10).map((item, index) => (
            <div key={item.id} className="centrality-item">
              <div className="centrality-rank">#{index + 1}</div>
              <div className="centrality-info">
                <div className="centrality-name">{item.label}</div>
                <div className="centrality-score">Score: {item.score}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);


export default GraphAnalysis;
