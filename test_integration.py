#!/usr/bin/env python3
"""
Script de prueba para la integración entre Graphiti MCP Server y Ollama
"""

import requests
import json
import time
from datetime import datetime

# Configuración
OLLAMA_URL = "http://192.168.100.20:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
GRAPHITI_MCP_URL = "http://localhost:8000/messages/"
SESSION_ID = "5b6d90707c01457593e5610fc2129c66"

def ask_ollama(prompt: str) -> str:
    """Hacer pregunta a Ollama en la VM"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )
        response.raise_for_status()
        return response.json().get("response", "Sin respuesta")
    except requests.RequestException as e:
        return f"Error al llamar a Ollama: {str(e)}"

def add_episode_to_graphiti(name: str, content: str, group_id: str = "test_integration"):
    """Agregar episodio a Graphiti usando MCP"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tool",
        "params": {
            "name": "add_episode",
            "input": {
                "name": name,
                "episode_body": content,
                "format": "text",
                "source_description": "Integración Ollama-Graphiti",
                "group_id": group_id
            }
        },
        "id": int(time.time())
    }
    
    try:
        response = requests.post(
            f"{GRAPHITI_MCP_URL}?session_id={SESSION_ID}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        return response.text
    except requests.RequestException as e:
        return f"Error al conectar con Graphiti: {str(e)}"

def search_in_graphiti(query: str, group_id: str = "test_integration"):
    """Buscar en Graphiti usando MCP"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tool",
        "params": {
            "name": "search_nodes",
            "input": {
                "query": query,
                "group_ids": [group_id],
                "max_nodes": 5
            }
        },
        "id": int(time.time())
    }
    
    try:
        response = requests.post(
            f"{GRAPHITI_MCP_URL}?session_id={SESSION_ID}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        return response.text
    except requests.RequestException as e:
        return f"Error al buscar en Graphiti: {str(e)}"

def main():
    print("=== PRUEBA DE INTEGRACIÓN OLLAMA + GRAPHITI ===")
    print(f"Fecha: {datetime.now()}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Modelo: {OLLAMA_MODEL}")
    print(f"Graphiti MCP URL: {GRAPHITI_MCP_URL}")
    print("=" * 60)
    
    # 1. Probar conexión con Ollama
    print("\\n1. Probando conexión con Ollama...")
    test_prompt = "¿Qué es un sistema de grafos de conocimiento?"
    ollama_response = ask_ollama(test_prompt)
    print(f"Pregunta: {test_prompt}")
    print(f"Respuesta: {ollama_response[:200]}...")
    
    # 2. Crear episodio en Graphiti con la respuesta de Ollama
    print("\\n2. Guardando respuesta en Graphiti...")
    episode_name = f"Ollama Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    episode_content = f"Pregunta: {test_prompt}\\n\\nRespuesta de Ollama ({OLLAMA_MODEL}): {ollama_response}"
    
    graphiti_result = add_episode_to_graphiti(episode_name, episode_content)
    print(f"Resultado de Graphiti: {graphiti_result}")
    
    # 3. Esperar un poco para el procesamiento
    print("\\n3. Esperando procesamiento...")
    time.sleep(10)
    
    # 4. Buscar en Graphiti
    print("\\n4. Buscando en Graphiti...")
    search_query = "grafos conocimiento"
    search_result = search_in_graphiti(search_query)
    print(f"Búsqueda '{search_query}': {search_result}")
    
    # 5. Hacer otra pregunta más específica
    print("\\n5. Segunda prueba con pregunta específica...")
    specific_prompt = "¿Cuáles son las ventajas de usar Neo4j para almacenar grafos de conocimiento?"
    specific_response = ask_ollama(specific_prompt)
    print(f"Pregunta específica: {specific_prompt}")
    print(f"Respuesta: {specific_response[:300]}...")
    
    # Guardar segunda respuesta
    episode_name_2 = f"Ollama Neo4j - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    episode_content_2 = f"Pregunta: {specific_prompt}\\n\\nRespuesta: {specific_response}"
    graphiti_result_2 = add_episode_to_graphiti(episode_name_2, episode_content_2)
    print(f"Segundo episodio guardado: {graphiti_result_2}")
    
    print("\\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    main()