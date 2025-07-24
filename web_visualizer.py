#!/usr/bin/env python3
"""
Visualizador Web para Grafos de Graphiti
Crea una aplicación web que muestra los grafos almacenados en Neo4j
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from neo4j import GraphDatabase
import uvicorn

app = FastAPI(title="Graphiti Graph Visualizer", version="1.0.0")

# Configuración desde variables de entorno
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "admin123")
GRAPHITI_MCP_URL = os.getenv("GRAPHITI_MCP_URL", "http://localhost:8000")

# Driver de Neo4j
driver = None

def get_neo4j_driver():
    """Obtener driver de Neo4j"""
    global driver
    if driver is None:
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            # Test connection
            driver.verify_connectivity()
        except Exception as e:
            print(f"Error conectando a Neo4j: {e}")
            driver = None
    return driver

@app.on_event("startup")
async def startup():
    """Inicializar conexiones"""
    print(f"Iniciando Graphiti Graph Visualizer...")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"Graphiti MCP: {GRAPHITI_MCP_URL}")
    
    # Test Neo4j connection
    neo4j_driver = get_neo4j_driver()
    if neo4j_driver:
        print("✅ Conexión a Neo4j exitosa")
    else:
        print("❌ Error conectando a Neo4j")

@app.on_event("shutdown")
async def shutdown():
    """Cerrar conexiones"""
    global driver
    if driver:
        driver.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con visualizador"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graphiti Graph Visualizer</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .controls {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .graph-container {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            #graph {{
                width: 100%;
                height: 600px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            
            .node {{
                fill: #69b3a2;
                stroke: #333;
                stroke-width: 2px;
                cursor: pointer;
            }}
            
            .node:hover {{
                fill: #ff6b6b;
            }}
            
            .link {{
                stroke: #999;
                stroke-opacity: 0.6;
                stroke-width: 2px;
            }}
            
            .node-label {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                fill: #333;
                text-anchor: middle;
                pointer-events: none;
            }}
            
            .button {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 4px;
                cursor: pointer;
            }}
            
            .button:hover {{
                background-color: #2980b9;
            }}
            
            .info-panel {{
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
            }}
            
            .stats {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }}
            
            .stat-card {{
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                flex: 1;
            }}
            
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
            }}
            
            .stat-label {{
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🕸️ Graphiti Graph Visualizer</h1>
            <p>Visualización interactiva de grafos de conocimiento almacenados en Neo4j</p>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="node-count">-</div>
                <div class="stat-label">Nodos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="edge-count">-</div>
                <div class="stat-label">Relaciones</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="episode-count">-</div>
                <div class="stat-label">Episodios</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="button" onclick="loadGraph()">🔄 Cargar Grafo</button>
            <button class="button" onclick="loadEpisodes()">📄 Ver Episodios</button>
            <button class="button" onclick="searchGraph()">🔍 Buscar</button>
            <button class="button" onclick="clearGraph()">🧹 Limpiar</button>
            
            <input type="text" id="searchInput" placeholder="Buscar nodos o episodios..." style="margin-left: 20px; padding: 8px; width: 300px;">
        </div>
        
        <div class="graph-container">
            <svg id="graph"></svg>
        </div>
        
        <div class="info-panel" id="info-panel">
            <h3>Información del Grafo</h3>
            <p>Selecciona un nodo para ver detalles</p>
        </div>

        <script>
            // Configuración D3.js
            const width = document.getElementById('graph').clientWidth;
            const height = 600;
            
            const svg = d3.select("#graph")
                .attr("width", width)
                .attr("height", height);
                
            const simulation = d3.forceSimulation()
                .force("link", d3.forceLink().id(d => d.id))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            let nodes = [];
            let links = [];
            
            // Función para cargar el grafo
            async function loadGraph() {{
                try {{
                    const response = await fetch('/api/graph');
                    const data = await response.json();
                    
                    if (data.success) {{
                        nodes = data.nodes;
                        links = data.links;
                        updateVisualization();
                        updateStats();
                    }} else {{
                        alert('Error cargando grafo: ' + data.error);
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
            
            // Función para cargar episodios
            async function loadEpisodes() {{
                try {{
                    const response = await fetch('/api/episodes');
                    const data = await response.json();
                    
                    document.getElementById('info-panel').innerHTML = 
                        '<h3>Episodios Recientes</h3>' + 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }} catch (error) {{
                    alert('Error cargando episodios: ' + error.message);
                }}
            }}
            
            // Función para buscar
            async function searchGraph() {{
                const query = document.getElementById('searchInput').value;
                if (!query) {{
                    alert('Ingresa un término de búsqueda');
                    return;
                }}
                
                try {{
                    const response = await fetch(`/api/search?q=${{encodeURIComponent(query)}}`);
                    const data = await response.json();
                    
                    document.getElementById('info-panel').innerHTML = 
                        '<h3>Resultados de Búsqueda: "' + query + '"</h3>' +
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }} catch (error) {{
                    alert('Error en búsqueda: ' + error.message);
                }}
            }}
            
            // Función para limpiar visualización
            function clearGraph() {{
                svg.selectAll("*").remove();
                nodes = [];
                links = [];
                updateStats();
            }}
            
            // Función para actualizar la visualización
            function updateVisualization() {{
                // Limpiar SVG
                svg.selectAll("*").remove();
                
                // Crear enlaces
                const link = svg.append("g")
                    .selectAll("line")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link");
                
                // Crear nodos
                const node = svg.append("g")
                    .selectAll("circle")
                    .data(nodes)
                    .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", d => Math.max(5, Math.min(20, (d.importance || 1) * 10)))
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended))
                    .on("click", function(event, d) {{
                        showNodeInfo(d);
                    }});
                
                // Etiquetas de nodos
                const label = svg.append("g")
                    .selectAll("text")
                    .data(nodes)
                    .enter().append("text")
                    .attr("class", "node-label")
                    .text(d => d.name || d.id);
                
                // Aplicar simulación
                simulation
                    .nodes(nodes)
                    .on("tick", ticked);
                    
                simulation.force("link")
                    .links(links);
                
                function ticked() {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                        
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                        
                    label
                        .attr("x", d => d.x)
                        .attr("y", d => d.y + 5);
                }}
            }}
            
            // Funciones de drag
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
            
            // Mostrar información del nodo
            function showNodeInfo(node) {{
                document.getElementById('info-panel').innerHTML = 
                    '<h3>Información del Nodo</h3>' +
                    '<p><strong>ID:</strong> ' + node.id + '</p>' +
                    '<p><strong>Nombre:</strong> ' + (node.name || 'N/A') + '</p>' +
                    '<p><strong>Tipo:</strong> ' + (node.labels ? node.labels.join(', ') : 'N/A') + '</p>' +
                    '<p><strong>Propiedades:</strong></p>' +
                    '<pre>' + JSON.stringify(node, null, 2) + '</pre>';
            }}
            
            // Actualizar estadísticas
            function updateStats() {{
                document.getElementById('node-count').textContent = nodes.length;
                document.getElementById('edge-count').textContent = links.length;
            }}
            
            // Cargar grafo al inicio
            window.onload = function() {{
                loadGraph();
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/graph")
async def get_graph():
    """Obtener datos del grafo desde Neo4j"""
    neo4j_driver = get_neo4j_driver()
    if not neo4j_driver:
        raise HTTPException(status_code=500, detail="No se puede conectar a Neo4j")
    
    try:
        with neo4j_driver.session() as session:
            # Obtener nodos
            nodes_result = session.run("""
                MATCH (n) 
                RETURN n.uuid as id, 
                       n.name as name, 
                       labels(n) as labels,
                       n.summary as summary,
                       n.created_at as created_at,
                       properties(n) as properties
                LIMIT 100
            """)
            
            nodes = []
            for record in nodes_result:
                node = {
                    "id": record["id"],
                    "name": record["name"] or record["id"][:8],
                    "labels": record["labels"],
                    "summary": record["summary"],
                    "created_at": record["created_at"],
                    "properties": dict(record["properties"]) if record["properties"] else {}
                }
                nodes.append(node)
            
            # Obtener relaciones
            links_result = session.run("""
                MATCH (a)-[r]->(b) 
                RETURN a.uuid as source, 
                       b.uuid as target, 
                       type(r) as relationship,
                       properties(r) as properties
                LIMIT 200
            """)
            
            links = []
            for record in links_result:
                link = {
                    "source": record["source"],
                    "target": record["target"],
                    "relationship": record["relationship"],
                    "properties": dict(record["properties"]) if record["properties"] else {}
                }
                links.append(link)
        
        return {
            "success": True,
            "nodes": nodes,
            "links": links,
            "stats": {
                "node_count": len(nodes),
                "link_count": len(links)
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/episodes")
async def get_episodes():
    """Obtener episodios recientes desde Graphiti MCP"""
    try:
        # Obtener nueva sesión
        sse_response = requests.get(f"{GRAPHITI_MCP_URL}/sse", timeout=10)
        session_line = [line for line in sse_response.text.split('\n') if 'session_id=' in line]
        
        if not session_line:
            return {"success": False, "error": "No se pudo obtener session ID"}
        
        session_id = session_line[0].split('session_id=')[1].strip()
        
        # Solicitar episodios
        payload = {
            "jsonrpc": "2.0",
            "method": "tool",
            "params": {
                "name": "get_episodes",
                "input": {"last_n": 10}
            },
            "id": 1
        }
        
        response = requests.post(
            f"{GRAPHITI_MCP_URL}/messages/?session_id={session_id}",
            json=payload,
            timeout=30
        )
        
        return {
            "success": True,
            "data": response.text,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/search")
async def search_graph(q: str):
    """Buscar en el grafo"""
    try:
        # Obtener nueva sesión
        sse_response = requests.get(f"{GRAPHITI_MCP_URL}/sse", timeout=10)
        session_line = [line for line in sse_response.text.split('\n') if 'session_id=' in line]
        
        if not session_line:
            return {"success": False, "error": "No se pudo obtener session ID"}
        
        session_id = session_line[0].split('session_id=')[1].strip()
        
        # Buscar nodos
        payload = {
            "jsonrpc": "2.0",
            "method": "tool",
            "params": {
                "name": "search_nodes",
                "input": {
                    "query": q,
                    "max_nodes": 10
                }
            },
            "id": 2
        }
        
        response = requests.post(
            f"{GRAPHITI_MCP_URL}/messages/?session_id={session_id}",
            json=payload,
            timeout=30
        )
        
        return {
            "success": True,
            "query": q,
            "results": response.text,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas del grafo"""
    neo4j_driver = get_neo4j_driver()
    if not neo4j_driver:
        raise HTTPException(status_code=500, detail="No se puede conectar a Neo4j")
    
    try:
        with neo4j_driver.session() as session:
            # Contar nodos por tipo
            node_stats = session.run("""
                MATCH (n) 
                RETURN labels(n) as labels, count(n) as count
            """)
            
            # Contar relaciones
            rel_stats = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as type, count(r) as count
            """)
            
            # Episodios
            episode_count = session.run("""
                MATCH (n:EpisodicNode) 
                RETURN count(n) as count
            """).single()
            
            node_types = {}
            for record in node_stats:
                labels = record["labels"]
                if labels:
                    key = ", ".join(labels)
                    node_types[key] = record["count"]
            
            rel_types = {}
            for record in rel_stats:
                rel_types[record["type"]] = record["count"]
        
        return {
            "success": True,
            "node_types": node_types,
            "relationship_types": rel_types,
            "episode_count": episode_count["count"] if episode_count else 0
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🚀 Iniciando Graphiti Graph Visualizer...")
    print(f"   Neo4j: {NEO4J_URI}")
    print(f"   Graphiti MCP: {GRAPHITI_MCP_URL}")
    print("   Abriendo en: http://localhost:8080")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        log_level="info"
    )