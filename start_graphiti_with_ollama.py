#!/usr/bin/env python3
"""
Script para iniciar Graphiti MCP con configuración para Ollama
"""
import os
import sys

# Configurar variables de entorno antes de importar cualquier módulo de Graphiti
os.environ['OPENAI_API_KEY'] = 'ollama-dummy-key'
os.environ['OPENAI_BASE_URL'] = 'http://192.168.100.20:11435/v1'
os.environ['MODEL_NAME'] = 'llama3.2:3b'
os.environ['NEO4J_URI'] = 'bolt://neo4j:7687'
os.environ['NEO4J_USER'] = 'neo4j'  
os.environ['NEO4J_PASSWORD'] = 'password'
os.environ['GRAPHITI_ENV'] = 'dev'

print("=== Configuración de Variables de Entorno ===")
print(f"OPENAI_API_KEY: {os.environ['OPENAI_API_KEY']}")
print(f"OPENAI_BASE_URL: {os.environ['OPENAI_BASE_URL']}")
print(f"MODEL_NAME: {os.environ['MODEL_NAME']}")
print(f"NEO4J_URI: {os.environ['NEO4J_URI']}")
print("=" * 50)

# Ahora importar e iniciar el servidor MCP
if __name__ == '__main__':
    # Agregar argumentos por defecto si no se proporcionan
    if len(sys.argv) == 1:
        sys.argv.extend(['--transport', 'sse', '--group-id', 'test_integration'])
    
    # Importar y ejecutar el servidor principal
    from graphiti_mcp_server import main
    main()