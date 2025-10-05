#!/usr/bin/env python3
"""
Knowledge Graph Implementation for NASA Space Biology Publications
Creates and manages a graph database of publications, authors, themes, and relationships
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import pandas as pd
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    node_type: str  # 'publication', 'author', 'journal', 'theme', 'keyword'
    properties: Dict[str, Any]
    weight: float = 1.0


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph"""
    source: str
    target: str
    relationship_type: str  # 'authored_by', 'published_in', 'has_theme', 'co_authors', etc.
    weight: float = 1.0
    properties: Dict[str, Any] = None


class NASAKnowledgeGraph:
    """Knowledge Graph for NASA Space Biology Publications"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.node_index = {}  # Fast lookup by ID
        self.edge_index = {}  # Fast lookup by relationship type
        self.statistics = {}
        
    def add_node(self, node: GraphNode):
        """Add a node to the graph"""
        self.graph.add_node(
            node.id,
            label=node.label,
            node_type=node.node_type,
            properties=node.properties,
            weight=node.weight
        )
        self.node_index[node.id] = node
        
    def add_edge(self, edge: GraphEdge):
        """Add an edge to the graph"""
        self.graph.add_edge(
            edge.source,
            edge.target,
            relationship_type=edge.relationship_type,
            weight=edge.weight,
            properties=edge.properties or {}
        )
        
        # Index by relationship type
        if edge.relationship_type not in self.edge_index:
            self.edge_index[edge.relationship_type] = []
        self.edge_index[edge.relationship_type].append(edge)
    
    def build_from_publications(self, publications_data: List[Dict]):
        """Build the knowledge graph from publication data"""
        logger.info(f"Building knowledge graph from {len(publications_data)} publications")
        
        # Track entities to avoid duplicates
        authors_seen = set()
        journals_seen = set()
        themes_seen = set()
        keywords_seen = set()
        
        for pub_data in publications_data:
            pub_id = f"pub_{pub_data['index']}"
            
            # Add publication node
            pub_node = GraphNode(
                id=pub_id,
                label=pub_data['title'][:100] + "..." if len(pub_data['title']) > 100 else pub_data['title'],
                node_type='publication',
                properties={
                    'title': pub_data['title'],
                    'abstract': pub_data.get('abstract', ''),
                    'summary': pub_data.get('summary', ''),
                    'impact': pub_data.get('impact', ''),
                    'doi': pub_data.get('doi'),
                    'publication_date': pub_data.get('publication_date'),
                    'url': pub_data.get('url', ''),
                    'original_title': pub_data.get('original_title', '')
                },
                weight=1.0
            )
            self.add_node(pub_node)
            
            # Add author nodes and relationships
            authors = pub_data.get('authors', [])
            if authors is None:
                authors = []
            for author in authors:
                if not author or author.strip() == '':
                    continue
                    
                author_id = f"author_{author.replace(' ', '_').replace(',', '').lower()}"
                
                if author_id not in authors_seen:
                    author_node = GraphNode(
                        id=author_id,
                        label=author,
                        node_type='author',
                        properties={'name': author},
                        weight=1.0
                    )
                    self.add_node(author_node)
                    authors_seen.add(author_id)
                
                # Add authored_by relationship
                authored_edge = GraphEdge(
                    source=pub_id,
                    target=author_id,
                    relationship_type='authored_by',
                    weight=1.0
                )
                self.add_edge(authored_edge)
            
            # Add journal node and relationship
            if pub_data.get('journal'):
                journal = pub_data['journal']
                journal_id = f"journal_{journal.replace(' ', '_').replace(',', '').lower()}"
                
                if journal_id not in journals_seen:
                    journal_node = GraphNode(
                        id=journal_id,
                        label=journal,
                        node_type='journal',
                        properties={'name': journal},
                        weight=1.0
                    )
                    self.add_node(journal_node)
                    journals_seen.add(journal_id)
                
                # Add published_in relationship
                published_edge = GraphEdge(
                    source=pub_id,
                    target=journal_id,
                    relationship_type='published_in',
                    weight=1.0
                )
                self.add_edge(published_edge)
            
            # Add theme node and relationship
            if pub_data.get('theme'):
                theme = pub_data['theme']
                theme_id = f"theme_{theme.replace(' ', '_').replace(',', '').lower()}"
                
                if theme_id not in themes_seen:
                    theme_node = GraphNode(
                        id=theme_id,
                        label=theme,
                        node_type='theme',
                        properties={'name': theme},
                        weight=1.0
                    )
                    self.add_node(theme_node)
                    themes_seen.add(theme_id)
                
                # Add has_theme relationship
                theme_edge = GraphEdge(
                    source=pub_id,
                    target=theme_id,
                    relationship_type='has_theme',
                    weight=1.0
                )
                self.add_edge(theme_edge)
            
            # Add keyword nodes and relationships
            keywords = pub_data.get('keywords', [])
            if keywords is None:
                keywords = []
            for keyword in keywords:
                if not keyword or keyword.strip() == '':
                    continue
                    
                keyword_id = f"keyword_{keyword.replace(' ', '_').replace(',', '').lower()}"
                
                if keyword_id not in keywords_seen:
                    keyword_node = GraphNode(
                        id=keyword_id,
                        label=keyword,
                        node_type='keyword',
                        properties={'name': keyword},
                        weight=1.0
                    )
                    self.add_node(keyword_node)
                    keywords_seen.add(keyword_id)
                
                # Add has_keyword relationship
                keyword_edge = GraphEdge(
                    source=pub_id,
                    target=keyword_id,
                    relationship_type='has_keyword',
                    weight=1.0
                )
                self.add_edge(keyword_edge)
        
        # Add co-authorship relationships
        self._add_co_authorship_relationships()
        
        # Calculate statistics
        self._calculate_statistics()
        
        logger.info(f"Knowledge graph built successfully!")
        logger.info(f"Nodes: {self.graph.number_of_nodes()}")
        logger.info(f"Edges: {self.graph.number_of_edges()}")
    
    def _add_co_authorship_relationships(self):
        """Add co-authorship relationships between authors"""
        logger.info("Adding co-authorship relationships...")
        
        # Get all publications
        publications = [node for node in self.graph.nodes(data=True) 
                       if node[1].get('node_type') == 'publication']
        
        for pub_id, pub_data in publications:
            # Get all authors of this publication
            authors = []
            for edge in self.graph.edges(pub_id, data=True):
                if edge[2].get('relationship_type') == 'authored_by':
                    authors.append(edge[1])
            
            # Add co-authorship edges between all pairs of authors
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    co_authored_edge = GraphEdge(
                        source=author1,
                        target=author2,
                        relationship_type='co_authors',
                        weight=1.0
                    )
                    self.add_edge(co_authored_edge)
    
    def _calculate_statistics(self):
        """Calculate graph statistics"""
        self.statistics = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': Counter([data.get('node_type', 'unknown') 
                                 for _, data in self.graph.nodes(data=True)]),
            'edge_types': Counter([data.get('relationship_type', 'unknown') 
                                 for _, _, data in self.graph.edges(data=True)]),
            'most_connected_authors': self._get_most_connected_authors(),
            'most_productive_journals': self._get_most_productive_journals(),
            'theme_distribution': self._get_theme_distribution(),
            'collaboration_network_stats': self._get_collaboration_stats()
        }
    
    def _get_most_connected_authors(self, top_n: int = 10):
        """Get authors with most co-authorship connections"""
        author_connections = defaultdict(int)
        
        for edge in self.graph.edges(data=True):
            if edge[2].get('relationship_type') == 'co_authors':
                author_connections[edge[0]] += 1
                author_connections[edge[1]] += 1
        
        return sorted(author_connections.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def _get_most_productive_journals(self, top_n: int = 10):
        """Get journals with most publications"""
        journal_publications = defaultdict(int)
        
        for edge in self.graph.edges(data=True):
            if edge[2].get('relationship_type') == 'published_in':
                journal_publications[edge[1]] += 1
        
        return sorted(journal_publications.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def _get_theme_distribution(self):
        """Get distribution of themes"""
        theme_counts = defaultdict(int)
        
        for edge in self.graph.edges(data=True):
            if edge[2].get('relationship_type') == 'has_theme':
                theme_counts[edge[1]] += 1
        
        return dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _get_collaboration_stats(self):
        """Get collaboration network statistics"""
        # Create a subgraph of just authors and co-authorship relationships
        author_nodes = [node for node in self.graph.nodes(data=True) 
                       if node[1].get('node_type') == 'author']
        author_subgraph = self.graph.subgraph([node[0] for node in author_nodes])
        
        # Remove non-co-authorship edges
        edges_to_remove = []
        for edge in author_subgraph.edges(data=True):
            if edge[2].get('relationship_type') != 'co_authors':
                edges_to_remove.append((edge[0], edge[1]))
        
        for edge in edges_to_remove:
            if author_subgraph.has_edge(edge[0], edge[1]):
                author_subgraph.remove_edge(edge[0], edge[1])
        
        # Convert to simple graph for clustering calculation
        simple_graph = nx.Graph(author_subgraph.to_undirected())
        
        return {
            'total_authors': len(author_nodes),
            'connected_components': nx.number_connected_components(simple_graph),
            'largest_component_size': len(max(nx.connected_components(simple_graph), key=len)) if simple_graph.number_of_nodes() > 0 else 0,
            'average_clustering': nx.average_clustering(simple_graph) if simple_graph.number_of_nodes() > 0 else 0
        }
    
    def get_author_collaboration_network(self, author_name: str, depth: int = 2):
        """Get collaboration network for a specific author"""
        author_id = f"author_{author_name.replace(' ', '_').replace(',', '').lower()}"
        
        if author_id not in self.graph:
            return None
        
        # Get all co-authors within specified depth
        visited = set()
        current_level = {author_id}
        result_nodes = {author_id}
        result_edges = []
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                if node in visited:
                    continue
                visited.add(node)
                
                for neighbor in self.graph.neighbors(node):
                    if self.graph[node][neighbor].get('relationship_type') == 'co_authors':
                        next_level.add(neighbor)
                        result_nodes.add(neighbor)
                        result_edges.append((node, neighbor))
            
            current_level = next_level
        
        return {
            'nodes': list(result_nodes),
            'edges': result_edges,
            'author_name': author_name
        }
    
    def get_theme_connections(self, theme_name: str):
        """Get publications and related themes for a specific theme"""
        theme_id = f"theme_{theme_name.replace(' ', '_').replace(',', '').lower()}"
        
        if theme_id not in self.graph:
            return None
        
        # Get all publications with this theme
        publications = []
        for edge in self.graph.edges(data=True):
            if (edge[2].get('relationship_type') == 'has_theme' and 
                edge[1] == theme_id):
                publications.append(edge[0])
        
        # Get related themes (themes that appear with the same publications)
        related_themes = set()
        for pub_id in publications:
            for edge in self.graph.edges(pub_id, data=True):
                if (edge[2].get('relationship_type') == 'has_theme' and 
                    edge[1] != theme_id):
                    related_themes.add(edge[1])
        
        return {
            'theme': theme_name,
            'publications': publications,
            'related_themes': list(related_themes),
            'publication_count': len(publications)
        }
    
    def get_keyword_co_occurrence(self, keyword: str, min_co_occurrence: int = 2):
        """Get keywords that frequently co-occur with the given keyword"""
        keyword_id = f"keyword_{keyword.replace(' ', '_').replace(',', '').lower()}"
        
        if keyword_id not in self.graph:
            return None
        
        # Find publications with this keyword
        publications_with_keyword = []
        for edge in self.graph.edges(data=True):
            if (edge[2].get('relationship_type') == 'has_keyword' and 
                edge[1] == keyword_id):
                publications_with_keyword.append(edge[0])
        
        # Count co-occurring keywords
        co_occurrence_count = defaultdict(int)
        for pub_id in publications_with_keyword:
            for edge in self.graph.edges(pub_id, data=True):
                if (edge[2].get('relationship_type') == 'has_keyword' and 
                    edge[1] != keyword_id):
                    co_occurrence_count[edge[1]] += 1
        
        # Filter by minimum co-occurrence
        filtered_co_occurrences = {
            kw_id: count for kw_id, count in co_occurrence_count.items() 
            if count >= min_co_occurrence
        }
        
        return {
            'keyword': keyword,
            'co_occurring_keywords': filtered_co_occurrences,
            'total_publications': len(publications_with_keyword)
        }
    
    def visualize_graph(self, output_path: str = "knowledge_graph.png", 
                       max_nodes: int = 100, layout: str = "spring"):
        """Create a visualization of the knowledge graph"""
        logger.info(f"Creating graph visualization with max {max_nodes} nodes")
        
        # Create a subgraph with the most important nodes
        if self.graph.number_of_nodes() > max_nodes:
            # Get top nodes by degree centrality
            centrality = nx.degree_centrality(self.graph)
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph([node[0] for node in top_nodes])
        else:
            subgraph = self.graph
        
        # Create the plot
        plt.figure(figsize=(20, 16))
        
        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(subgraph, k=3, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(subgraph)
        elif layout == "hierarchical":
            pos = nx.nx_agraph.graphviz_layout(subgraph, prog='dot')
        else:
            pos = nx.spring_layout(subgraph)
        
        # Color nodes by type
        node_colors = []
        node_types = []
        for node in subgraph.nodes(data=True):
            node_type = node[1].get('node_type', 'unknown')
            node_types.append(node_type)
            if node_type == 'publication':
                node_colors.append('#FF6B6B')  # Red
            elif node_type == 'author':
                node_colors.append('#4ECDC4')  # Teal
            elif node_type == 'journal':
                node_colors.append('#45B7D1')  # Blue
            elif node_type == 'theme':
                node_colors.append('#96CEB4')  # Green
            elif node_type == 'keyword':
                node_colors.append('#FFEAA7')  # Yellow
            else:
                node_colors.append('#DDA0DD')  # Plum
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, 
                              node_size=100, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, alpha=0.3, width=0.5)
        
        # Add labels for important nodes
        important_nodes = {}
        for node in subgraph.nodes(data=True):
            node_type = node[1].get('node_type', 'unknown')
            if node_type in ['author', 'theme', 'journal']:
                important_nodes[node[0]] = node[1].get('label', node[0])
        
        nx.draw_networkx_labels(subgraph, pos, important_nodes, font_size=8)
        
        # Create legend
        legend_elements = [
            mpatches.Patch(color='#FF6B6B', label='Publications'),
            mpatches.Patch(color='#4ECDC4', label='Authors'),
            mpatches.Patch(color='#45B7D1', label='Journals'),
            mpatches.Patch(color='#96CEB4', label='Themes'),
            mpatches.Patch(color='#FFEAA7', label='Keywords')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title(f"NASA Space Biology Knowledge Graph\n{self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges", 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Graph visualization saved to {output_path}")
    
    def export_to_json(self, output_path: str):
        """Export the knowledge graph to JSON format"""
        graph_data = {
            'nodes': [],
            'edges': [],
            'statistics': self.statistics
        }
        
        # Export nodes
        for node_id, node_data in self.graph.nodes(data=True):
            graph_data['nodes'].append({
                'id': node_id,
                'label': node_data.get('label', ''),
                'type': node_data.get('node_type', ''),
                'properties': node_data.get('properties', {}),
                'weight': node_data.get('weight', 1.0)
            })
        
        # Export edges
        for source, target, edge_data in self.graph.edges(data=True):
            graph_data['edges'].append({
                'source': source,
                'target': target,
                'relationship_type': edge_data.get('relationship_type', ''),
                'weight': edge_data.get('weight', 1.0),
                'properties': edge_data.get('properties', {})
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Knowledge graph exported to {output_path}")
    
    def print_statistics(self):
        """Print detailed statistics about the knowledge graph"""
        print("\n" + "="*60)
        print("NASA SPACE BIOLOGY KNOWLEDGE GRAPH STATISTICS")
        print("="*60)
        
        print(f"\n📊 BASIC STATISTICS:")
        print(f"   Total Nodes: {self.statistics['total_nodes']}")
        print(f"   Total Edges: {self.statistics['total_edges']}")
        
        print(f"\n🏷️  NODE TYPES:")
        for node_type, count in self.statistics['node_types'].items():
            print(f"   {node_type.title()}: {count}")
        
        print(f"\n🔗 RELATIONSHIP TYPES:")
        for edge_type, count in self.statistics['edge_types'].items():
            print(f"   {edge_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n👥 TOP CONNECTED AUTHORS:")
        for author_id, connections in self.statistics['most_connected_authors'][:5]:
            author_name = self.node_index[author_id].label
            print(f"   {author_name}: {connections} connections")
        
        print(f"\n📚 MOST PRODUCTIVE JOURNALS:")
        for journal_id, count in self.statistics['most_productive_journals'][:5]:
            journal_name = self.node_index[journal_id].label
            print(f"   {journal_name}: {count} publications")
        
        print(f"\n🎯 THEME DISTRIBUTION:")
        for theme_id, count in list(self.statistics['theme_distribution'].items())[:5]:
            theme_name = self.node_index[theme_id].label
            print(f"   {theme_name}: {count} publications")
        
        print(f"\n🤝 COLLABORATION NETWORK:")
        collab_stats = self.statistics['collaboration_network_stats']
        print(f"   Total Authors: {collab_stats['total_authors']}")
        print(f"   Connected Components: {collab_stats['connected_components']}")
        print(f"   Largest Component Size: {collab_stats['largest_component_size']}")
        print(f"   Average Clustering: {collab_stats['average_clustering']:.3f}")
        
        print("\n" + "="*60)


def main():
    """Main function to build and analyze the knowledge graph"""
    # Load publication data
    publications_file = "../data/scraped_publications.json"
    
    if not Path(publications_file).exists():
        logger.error(f"Publications file not found: {publications_file}")
        return
    
    with open(publications_file, 'r', encoding='utf-8') as f:
        publications_data = json.load(f)
    
    # Build knowledge graph
    kg = NASAKnowledgeGraph()
    kg.build_from_publications(publications_data)
    
    # Print statistics
    kg.print_statistics()
    
    # Export to JSON
    kg.export_to_json("../data/knowledge_graph/knowledge_graph.json")
    
    # Create visualization
    kg.visualize_graph("../data/knowledge_graph/knowledge_graph_visualization.png")
    
    # Example queries
    print(f"\n🔍 EXAMPLE QUERIES:")
    
    # Get collaboration network for a specific author
    if kg.statistics['most_connected_authors']:
        top_author_id = kg.statistics['most_connected_authors'][0][0]
        top_author_name = kg.node_index[top_author_id].label
        collab_network = kg.get_author_collaboration_network(top_author_name, depth=2)
        if collab_network:
            print(f"\n   Collaboration network for {top_author_name}:")
            print(f"   Connected to {len(collab_network['nodes'])-1} other authors")
    
    # Get theme connections
    if kg.statistics['theme_distribution']:
        top_theme_id = list(kg.statistics['theme_distribution'].keys())[0]
        top_theme_name = kg.node_index[top_theme_id].label
        theme_connections = kg.get_theme_connections(top_theme_name)
        if theme_connections:
            print(f"\n   Theme '{top_theme_name}' connections:")
            print(f"   {theme_connections['publication_count']} publications")
            print(f"   {len(theme_connections['related_themes'])} related themes")


if __name__ == "__main__":
    main()
