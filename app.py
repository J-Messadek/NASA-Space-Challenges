#!/usr/bin/env python3
"""
Graph API Service for NASA Space Biology Knowledge Graph
Provides REST API endpoints for graph queries and visualization
"""

import json
import logging
import os
import dotenv
from pathlib import Path
from typing import Optional
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import networkx as nx
from scripts.build_knowledge_graph import NASAKnowledgeGraph

# Import semantic search functionality
from scripts.simple_semantic_search import load_embeddings, semantic_search

# Load environment variables from .env file in development
# In production, environment variables are set by the platform
if os.path.exists('.env'):
    dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Debug environment variable loading
api_key_available = bool(os.getenv("GOOGLE_AI_API_KEY"))
logger.info(f"Google AI API key available: {api_key_available}")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global knowledge graph instance
kg: Optional[NASAKnowledgeGraph] = None

# Global semantic search data
semantic_publications = []
semantic_embeddings = []


def load_knowledge_graph():
    """Load the knowledge graph from JSON file"""
    global kg
    
    kg_file = Path("./data/knowledge_graph/knowledge_graph.json")
    if not kg_file.exists():
        logger.error("Knowledge graph not found. Please run knowledge_graph.py first.")
        return False
    
    try:
        with open(kg_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # Reconstruct the graph from JSON data
        kg = NASAKnowledgeGraph()
        
        # Add nodes
        for node_data in graph_data['nodes']:
            from scripts.build_knowledge_graph import GraphNode
            node = GraphNode(
                id=node_data['id'],
                label=node_data['label'],
                node_type=node_data['type'],
                properties=node_data['properties'],
                weight=node_data.get('weight', 1.0)
            )
            kg.add_node(node)
        
        # Add edges
        for edge_data in graph_data['edges']:
            from scripts.build_knowledge_graph import GraphEdge
            edge = GraphEdge(
                source=edge_data['source'],
                target=edge_data['target'],
                relationship_type=edge_data['relationship_type'],
                weight=edge_data.get('weight', 1.0),
                properties=edge_data.get('properties', {})
            )
            kg.add_edge(edge)
        
        kg.statistics = graph_data.get('statistics', {})
        logger.info("Knowledge graph loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading knowledge graph: {e}")
        return False


def load_semantic_search_data():
    """Load semantic search data (publications and embeddings)"""
    global semantic_publications, semantic_embeddings
    
    embeddings_file = Path("./embeddings.json")
    if not embeddings_file.exists():
        logger.warning("Semantic search embeddings not found. Semantic search will be disabled.")
        return False
    
    try:
        semantic_publications, semantic_embeddings = load_embeddings(str(embeddings_file))
        logger.info(f"Loaded {len(semantic_publications)} publications with embeddings for semantic search")
        return True
    except Exception as e:
        logger.error(f"Error loading semantic search data: {e}")
        return False


@app.route('/api/graph/statistics', methods=['GET'])
def get_graph_statistics():
    """Get overall graph statistics"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    return jsonify({
        'success': True,
        'data': kg.statistics
    })


@app.route('/api/graph/author/<author_name>', methods=['GET'])
def get_author_info(author_name):
    """Get information about a specific author"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    author_id = f"author_{author_name.replace(' ', '_').replace(',', '').lower()}"
    
    if author_id not in kg.graph:
        return jsonify({'error': 'Author not found'}), 404
    
    # Get author's publications
    publications = []
    for edge in kg.graph.edges(data=True):
        if (edge[2].get('relationship_type') == 'authored_by' and 
            edge[1] == author_id):
            pub_id = edge[0]
            pub_data = kg.graph.nodes[pub_id]
            publications.append({
                'id': pub_id,
                'title': pub_data.get('label', ''),
                'properties': pub_data.get('properties', {})
            })
    
    # Get co-authors
    co_authors = set()
    for edge in kg.graph.edges(data=True):
        if (edge[2].get('relationship_type') == 'co_authors' and 
            edge[0] == author_id):
            co_author_id = edge[1]
            co_author_data = kg.graph.nodes[co_author_id]
            co_authors.add(co_author_data.get('label', co_author_id))
    
    return jsonify({
        'success': True,
        'data': {
            'author_name': author_name,
            'publications': publications,
            'co_authors': list(co_authors),
            'publication_count': len(publications),
            'collaboration_count': len(co_authors)
        }
    })


@app.route('/api/graph/author/<author_name>/collaboration-network', methods=['GET'])
def get_author_collaboration_network(author_name):
    """Get collaboration network for a specific author"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    depth = request.args.get('depth', 2, type=int)
    network = kg.get_author_collaboration_network(author_name, depth)
    
    if not network:
        return jsonify({'error': 'Author not found'}), 404
    
    # Convert node IDs to readable names
    nodes = []
    for node_id in network['nodes']:
        node_data = kg.graph.nodes[node_id]
        nodes.append({
            'id': node_id,
            'label': node_data.get('label', node_id),
            'type': node_data.get('node_type', 'unknown')
        })
    
    edges = []
    for source, target in network['edges']:
        edges.append({
            'source': source,
            'target': target,
            'relationship_type': 'co_authors'
        })
    
    return jsonify({
        'success': True,
        'data': {
            'author_name': author_name,
            'nodes': nodes,
            'edges': edges,
            'depth': depth
        }
    })


@app.route('/api/graph/theme/<theme_name>', methods=['GET'])
def get_theme_info(theme_name):
    """Get information about a specific theme"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    theme_connections = kg.get_theme_connections(theme_name)
    
    if not theme_connections:
        return jsonify({'error': 'Theme not found'}), 404
    
    # Get publication details
    publications = []
    for pub_id in theme_connections['publications']:
        pub_data = kg.graph.nodes[pub_id]
        publications.append({
            'id': pub_id,
            'title': pub_data.get('label', ''),
            'properties': pub_data.get('properties', {})
        })
    
    # Get related theme details
    related_themes = []
    for theme_id in theme_connections['related_themes']:
        theme_data = kg.graph.nodes[theme_id]
        related_themes.append({
            'id': theme_id,
            'name': theme_data.get('label', theme_id)
        })
    
    return jsonify({
        'success': True,
        'data': {
            'theme': theme_name,
            'publications': publications,
            'related_themes': related_themes,
            'publication_count': theme_connections['publication_count']
        }
    })


@app.route('/api/graph/keyword/<keyword>', methods=['GET'])
def get_keyword_info(keyword):
    """Get information about a specific keyword"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    min_co_occurrence = request.args.get('min_co_occurrence', 2, type=int)
    co_occurrence_data = kg.get_keyword_co_occurrence(keyword, min_co_occurrence)
    
    if not co_occurrence_data:
        return jsonify({'error': 'Keyword not found'}), 404
    
    # Get co-occurring keyword details
    co_occurring_keywords = []
    for kw_id, count in co_occurrence_data['co_occurring_keywords'].items():
        kw_data = kg.graph.nodes[kw_id]
        co_occurring_keywords.append({
            'id': kw_id,
            'name': kw_data.get('label', kw_id),
            'co_occurrence_count': count
        })
    
    # Sort by co-occurrence count
    co_occurring_keywords.sort(key=lambda x: x['co_occurrence_count'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': {
            'keyword': keyword,
            'co_occurring_keywords': co_occurring_keywords,
            'total_publications': co_occurrence_data['total_publications'],
            'min_co_occurrence': min_co_occurrence
        }
    })


@app.route('/api/graph/search', methods=['GET'])
def search_graph():
    """Search for nodes in the graph"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    query = request.args.get('q', '').lower()
    node_type = request.args.get('type', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    results = []
    for node_id, node_data in kg.graph.nodes(data=True):
        if node_type and node_data.get('node_type') != node_type:
            continue
        
        label = node_data.get('label', '').lower()
        if query in label:
            results.append({
                'id': node_id,
                'label': node_data.get('label', ''),
                'type': node_data.get('node_type', ''),
                'properties': node_data.get('properties', {})
            })
    
    # Sort by relevance (exact match first, then partial match)
    results.sort(key=lambda x: (
        0 if query == x['label'].lower() else 1,
        -len(x['label'])
    ))
    
    return jsonify({
        'success': True,
        'data': {
            'query': query,
            'results': results[:limit],
            'total_found': len(results)
        }
    })


@app.route('/api/graph/visualization', methods=['GET'])
def get_graph_visualization():
    """Generate and return graph visualization"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    max_nodes = request.args.get('max_nodes', 100, type=int)
    layout = request.args.get('layout', 'spring')
    
    try:
        output_path = f"./data/knowledge_graph/graph_visualization_{max_nodes}_{layout}.png"
        kg.visualize_graph(output_path, max_nodes, layout)
        
        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        return jsonify({'error': 'Failed to generate visualization'}), 500


@app.route('/api/graph/path/<source_id>/<target_id>', methods=['GET'])
def get_shortest_path(source_id, target_id):
    """Get shortest path between two nodes"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    if source_id not in kg.graph or target_id not in kg.graph:
        return jsonify({'error': 'One or both nodes not found'}), 404
    
    try:
        # Convert to undirected graph for path finding
        undirected_graph = kg.graph.to_undirected()
        
        if nx.has_path(undirected_graph, source_id, target_id):
            path = nx.shortest_path(undirected_graph, source_id, target_id)
            
            # Get path details
            path_nodes = []
            for node_id in path:
                node_data = kg.graph.nodes[node_id]
                path_nodes.append({
                    'id': node_id,
                    'label': node_data.get('label', ''),
                    'type': node_data.get('node_type', '')
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'source': source_id,
                    'target': target_id,
                    'path': path_nodes,
                    'path_length': len(path) - 1
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'source': source_id,
                    'target': target_id,
                    'path': [],
                    'path_length': -1,
                    'message': 'No path found between nodes'
                }
            })
    
    except Exception as e:
        logger.error(f"Error finding path: {e}")
        return jsonify({'error': 'Failed to find path'}), 500


@app.route('/api/graph/centrality', methods=['GET'])
def get_centrality_measures():
    """Get centrality measures for the graph"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    try:
        # Calculate centrality measures
        degree_centrality = nx.degree_centrality(kg.graph)
        betweenness_centrality = nx.betweenness_centrality(kg.graph)
        closeness_centrality = nx.closeness_centrality(kg.graph)
        
        # Get top nodes by each measure
        top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        top_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Convert to readable format
        def format_centrality_results(centrality_results):
            formatted = []
            for node_id, score in centrality_results:
                node_data = kg.graph.nodes[node_id]
                formatted.append({
                    'id': node_id,
                    'label': node_data.get('label', ''),
                    'type': node_data.get('node_type', ''),
                    'score': round(score, 4)
                })
            return formatted
        
        return jsonify({
            'success': True,
            'data': {
                'degree_centrality': format_centrality_results(top_degree),
                'betweenness_centrality': format_centrality_results(top_betweenness),
                'closeness_centrality': format_centrality_results(top_closeness)
            }
        })
    
    except Exception as e:
        logger.error(f"Error calculating centrality: {e}")
        return jsonify({'error': 'Failed to calculate centrality measures'}), 500


@app.route('/api/graph/data', methods=['GET'])
def get_graph_data():
    """Get the complete graph data as JSON for frontend consumption"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    try:
        # Convert the graph to JSON format
        nodes = []
        for node_id, node_data in kg.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'label': node_data.get('label', ''),
                'type': node_data.get('node_type', ''),
                'weight': node_data.get('weight', 1.0),
                'properties': node_data.get('properties', {})
            })
        
        edges = []
        for source, target, edge_data in kg.graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'relationship_type': edge_data.get('relationship_type', ''),
                'weight': edge_data.get('weight', 1.0),
                'properties': edge_data.get('properties', {})
            })
        
        return jsonify({
            'success': True,
            'nodes': nodes,
            'edges': edges,
            'statistics': kg.statistics
        })
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        return jsonify({'error': 'Failed to get graph data'}), 500


@app.route('/api/graph/export', methods=['GET'])
def export_graph():
    """Export the complete graph data as a downloadable file"""
    if not kg:
        return jsonify({'error': 'Knowledge graph not loaded'}), 500
    
    try:
        kg.export_to_json("./data/knowledge_graph/exported_knowledge_graph.json")
        return send_file("./data/knowledge_graph/exported_knowledge_graph.json", 
                        mimetype='application/json',
                        as_attachment=True,
                        download_name='nasa_knowledge_graph.json')
    except Exception as e:
        logger.error(f"Error exporting graph: {e}")
        return jsonify({'error': 'Failed to export graph'}), 500


@app.route('/api/search/semantic', methods=['POST'])
def semantic_search_endpoint():
    """Semantic search endpoint for publications - called when keyword search fails"""
    if not semantic_publications or not semantic_embeddings:
        return jsonify({'error': 'Semantic search not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        query = data['query']
        limit = data.get('limit', 20)
        
        # Get API key from environment
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            return jsonify({'error': 'Google AI API key not configured'}), 500
        
        # Perform semantic search
        results = semantic_search(
            query, 
            semantic_publications, 
            semantic_embeddings, 
            api_key, 
            limit
        )
        
        # Filter results to only include those with similarity score >= 0.80 (80%)
        filtered_results = [
            result for result in results 
            if result.get('similarity_score', 0) >= 0.80
        ]
        
        return jsonify({
            'success': True,
            'query': query,
            'results': filtered_results,
            'total_found': len(filtered_results),
            'search_type': 'semantic',
            'min_similarity_threshold': 0.80
        })
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return jsonify({'error': 'Semantic search failed'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'graph_loaded': kg is not None,
        'semantic_search_loaded': len(semantic_publications) > 0,
        'google_ai_api_key_available': bool(os.getenv("GOOGLE_AI_API_KEY")),
        'nodes': kg.graph.number_of_nodes() if kg else 0,
        'edges': kg.graph.number_of_edges() if kg else 0,
        'semantic_publications': len(semantic_publications)
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Main function to start the API server"""
    logger.info("Starting NASA Knowledge Graph API Server...")
    
    # Load knowledge graph
    if not load_knowledge_graph():
        logger.error("Failed to load knowledge graph. Exiting.")
        return
    
    logger.info("Knowledge graph loaded successfully")
    logger.info(f"Graph contains {kg.graph.number_of_nodes()} nodes and {kg.graph.number_of_edges()} edges")
    
    # Load semantic search data
    load_semantic_search_data()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    main()
