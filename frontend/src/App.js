import React, { useState, useEffect } from 'react';
import { Search, Filter, ExternalLink, Users, Calendar, BookOpen, Target, Tag, ChevronLeft, ChevronRight, Network, BarChart3 } from 'lucide-react';
import GraphVisualization from './components/GraphVisualization';
import GraphAnalysis from './components/GraphAnalysis';
import './App.css';

function App() {
  const [publications, setPublications] = useState([]);
  const [filteredPublications, setFilteredPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [themeFilter, setThemeFilter] = useState('');
  const [journalFilter, setJournalFilter] = useState('');
  const [yearFilter, setYearFilter] = useState('');
  const [authorFilter, setAuthorFilter] = useState('');
  const [semanticSearching, setSemanticSearching] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  
  // Navigation state
  const [activeView, setActiveView] = useState('publications'); // 'publications', 'graph', 'analysis'

  const apiUrl =  process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Load publications data
  useEffect(() => {
    const loadPublications = async () => {
      try {
        // In a real app, this would be an API call
        // For now, we'll load from the JSON file
        const response = await fetch('/nasa_space_biology_publications.json');
        if (response.ok) {
          const data = await response.json();
          setPublications(data);
          setFilteredPublications(data);
        } else {
          // Fallback: try to load from public folder
          const fallbackResponse = await fetch('./nasa_space_biology_publications.json');
          if (fallbackResponse.ok) {
            const data = await fallbackResponse.json();
            setPublications(data);
            setFilteredPublications(data);
          }
        }
      } catch (error) {
        console.error('Error loading publications:', error);
        // For development, you can add sample data here
        setPublications([]);
        setFilteredPublications([]);
      } finally {
        setLoading(false);
      }
    };

    loadPublications();
  }, []);

  // Filter publications based on filters only (search is handled by button click)
  useEffect(() => {
    let filtered = publications;

    // Theme filter
    if (themeFilter) {
      filtered = filtered.filter(pub => 
        pub.theme.toLowerCase().includes(themeFilter.toLowerCase())
      );
    }

    // Journal filter
    if (journalFilter) {
      filtered = filtered.filter(pub => 
        pub.journal && pub.journal.toLowerCase().includes(journalFilter.toLowerCase())
      );
    }

    // Year filter
    if (yearFilter) {
      filtered = filtered.filter(pub => {
        const date = pub.publication_date;
        if (!date) return false;
        const year = date.split(' ')[0]; // Extract year from "2025 Mar 27" format
        return year === yearFilter;
      });
    }

    // Author filter
    if (authorFilter) {
      filtered = filtered.filter(pub => 
        pub.authors.some(author => author.toLowerCase().includes(authorFilter.toLowerCase()))
      );
    }

    setFilteredPublications(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [publications, themeFilter, journalFilter, yearFilter, authorFilter]);

  // Get unique values for filter options
  const themes = [...new Set(publications.map(pub => pub.theme).filter(Boolean))].sort();
  const journals = [...new Set(publications.map(pub => pub.journal).filter(Boolean))].sort();
  const years = [...new Set(publications.map(pub => {
    const date = pub.publication_date;
    if (!date) return null;
    const year = date.split(' ')[0]; // Split by space, get first part
    return /^\d{4}$/.test(year) ? year : null; // Only valid 4-digit years
  }).filter(Boolean))].sort((a, b) => b - a);
  const authors = [...new Set(publications.flatMap(pub => pub.authors).filter(Boolean))].sort();

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearch = () => {
    if (!searchTerm.trim()) return;
    
    // Perform keyword search first
    let filtered = publications;
    const searchLower = searchTerm.toLowerCase();
    filtered = filtered.filter(pub => 
      pub.title.toLowerCase().includes(searchLower) ||
      pub.summary.toLowerCase().includes(searchLower) ||
      pub.impact.toLowerCase().includes(searchLower) ||
      pub.authors.some(author => author.toLowerCase().includes(searchLower)) ||
      pub.keywords.some(keyword => keyword.toLowerCase().includes(searchLower))
    );
    
    if (filtered.length === 0) {
      // If no keyword results, try semantic search
      performSemanticSearch(searchTerm);
    } else {
      setFilteredPublications(filtered);
      setCurrentPage(1);
    }
  };

  const handleThemeFilterChange = (e) => {
    setThemeFilter(e.target.value);
  };

  const handleJournalFilterChange = (e) => {
    setJournalFilter(e.target.value);
  };

  const handleYearFilterChange = (e) => {
    setYearFilter(e.target.value);
  };

  const handleAuthorFilterChange = (e) => {
    setAuthorFilter(e.target.value);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setThemeFilter('');
    setJournalFilter('');
    setYearFilter('');
    setAuthorFilter('');
    setSemanticSearching(false);
    // Reset to show all publications
    setFilteredPublications(publications);
    setCurrentPage(1);
  };

  // Pagination calculations
  const totalPages = Math.ceil(filteredPublications.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentPublications = filteredPublications.slice(startIndex, endIndex);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Semantic search function
  const performSemanticSearch = async (query) => {
    if (!query.trim()) return;
    
    setSemanticSearching(true);
    
    try {
      const response = await fetch(`${apiUrl}/api/search/semantic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          limit: 50
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.results.length > 0) {
          setFilteredPublications(data.results);
        } else {
          setFilteredPublications([]);
        }
      } else {
        console.error('Semantic search failed:', response.statusText);
        setFilteredPublications([]);
      }
    } catch (error) {
      console.error('Error performing semantic search:', error);
      setFilteredPublications([]);
    } finally {
      setSemanticSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="container">
          <h2>Loading NASA Space Biology Publications...</h2>
          <p>Please wait while we load the research data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <img src="/bioverses_full.png" alt="Bioverses Logo" className="logo-image" />
              NASA Space Biology Publications
            </div>
            
            {/* Navigation */}
            <nav className="main-nav">
              <button 
                className={`nav-btn ${activeView === 'publications' ? 'active' : ''}`}
                onClick={() => setActiveView('publications')}
              >
                <BookOpen size={16} />
                Publications
              </button>
              <button 
                className={`nav-btn ${activeView === 'graph' ? 'active' : ''}`}
                onClick={() => setActiveView('graph')}
              >
                <Network size={16} />
                Knowledge Graph
              </button>
              <button 
                className={`nav-btn ${activeView === 'analysis' ? 'active' : ''}`}
                onClick={() => setActiveView('analysis')}
              >
                <BarChart3 size={16} />
                Analysis
              </button>
            </nav>
          </div>
        </div>
      </header>

      <div className="container">
        {/* Render different views based on activeView */}
        {activeView === 'publications' && (
          <>
            {/* Search and Filter Section */}
            <section className="search-section">
              {/* Search Bar - Full Width */}
              <div className="search-container">
                <div className="search-input-container">
                  <Search size={20} className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search publications by title, authors, keywords, or content..."
                    value={searchTerm}
                    onChange={handleSearchChange}
                    className="search-input"
                    disabled={semanticSearching}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch();
                      }
                    }}
                  />
                  <button 
                    className="search-button"
                    onClick={handleSearch}
                    disabled={semanticSearching || !searchTerm.trim()}
                  >
                    {semanticSearching ? (
                      <div className="spinner"></div>
                    ) : (
                      <Search size={16} />
                    )}
                  </button>
                </div>
              </div>
              
              {/* Filters Row */}
              <div className="filters-row">
                <div className="filter-container">
                  <select
                    value={themeFilter}
                    onChange={handleThemeFilterChange}
                    className="filter-select"
                  >
                    <option value="">All Themes</option>
                    {themes.map(theme => (
                      <option key={theme} value={theme}>{theme}</option>
                    ))}
                  </select>
                  
                  <select
                    value={journalFilter}
                    onChange={handleJournalFilterChange}
                    className="filter-select"
                  >
                    <option value="">All Journals</option>
                    {journals.map(journal => (
                      <option key={journal} value={journal}>{journal}</option>
                    ))}
                  </select>

                  <select
                    value={yearFilter}
                    onChange={handleYearFilterChange}
                    className="filter-select"
                  >
                    <option value="">All Years</option>
                    {years.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>

                  <select
                    value={authorFilter}
                    onChange={handleAuthorFilterChange}
                    className="filter-select"
                  >
                    <option value="">All Authors</option>
                    {authors.map(author => (
                      <option key={author} value={author}>{author}</option>
                    ))}
                  </select>
                </div>
                
                {/* Clear Button - Bottom Right */}
                {(searchTerm || themeFilter || journalFilter || yearFilter || authorFilter) && (
                  <button onClick={clearFilters} className="btn btn-secondary clear-filters-btn">
                    Clear Filters
                  </button>
                )}
              </div>
            </section>

            {/* Publications List */}
            <section className="publications-container">
              {filteredPublications.length === 0 ? (
                <div className="empty-state">
                  <h3>No Publications Found</h3>
                  <p>Try adjusting your search terms or filters to discover more research publications.</p>
                </div>
              ) : (
                <>
                  <div className="publications-grid">
                    {currentPublications.map((publication) => (
                      <PublicationCard 
                        key={publication.index} 
                        publication={publication}
                      />
                    ))}
                  </div>
                  
                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="pagination">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="pagination-btn"
                      >
                        <ChevronLeft size={16} />
                        Previous
                      </button>
                      
                      <div className="pagination-info">
                        Page {currentPage} of {totalPages} ({filteredPublications.length} total results)
                      </div>
                      
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="pagination-btn"
                      >
                        Next
                        <ChevronRight size={16} />
                      </button>
                    </div>
                  )}
                </>
              )}
            </section>
          </>
        )}

        {activeView === 'graph' && <GraphVisualization />}
        {activeView === 'analysis' && <GraphAnalysis />}
      </div>
    </div>
  );
}

// Publication Card Component
function PublicationCard({ publication }) {
  const formatAuthors = (authors) => {
    if (!authors || authors.length === 0) return 'Unknown Authors';
    if (authors.length <= 3) return authors.join(', ');
    return `${authors.slice(0, 3).join(', ')} et al.`;
  };

  const formatDate = (date) => {
    if (!date) return 'Unknown Date';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <article className="publication-card">
      <div className="publication-header">
        <h2 className="publication-title">{publication.title}</h2>
        <div className="publication-theme">{publication.theme}</div>
      </div>
      
      <div className="publication-meta">
        <div className="meta-item">
          <Users size={16} />
          {formatAuthors(publication.authors)}
        </div>
        {publication.journal && (
          <div className="meta-item">
            <BookOpen size={16} />
            {publication.journal}
          </div>
        )}
        {publication.publication_date && (
          <div className="meta-item">
            <Calendar size={16} />
            {formatDate(publication.publication_date)}
          </div>
        )}
        {publication.doi && (
          <div className="meta-item">
            <Tag size={16} />
            DOI: {publication.doi}
          </div>
        )}
      </div>
      
      {publication.summary && (
        <div className="publication-summary">
          {publication.summary}
        </div>
      )}
      
      {publication.impact && (
        <div className="publication-impact">
          <div className="impact-label">
            <Target size={16} />
            Research Impact
          </div>
          {publication.impact}
        </div>
      )}
      
      {publication.keywords && publication.keywords.length > 0 && (
        <div className="publication-keywords">
          {publication.keywords.map((keyword, index) => (
            <span key={index} className="keyword">{keyword}</span>
          ))}
        </div>
      )}
      
      <div className="publication-actions">
        <a
          href={publication.url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary btn-full-width"
        >
          <ExternalLink size={16} />
          Read Full Paper
        </a>
      </div>
    </article>
  );
}

export default App;
