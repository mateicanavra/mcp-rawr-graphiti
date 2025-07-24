#!/bin/bash

echo "=== Configurando Graphiti MCP para usar Ollama embeddings ==="

# Configurar variables de entorno para usar el proxy local
export OPENAI_API_KEY="ollama-dummy-key"
export OPENAI_BASE_URL="http://localhost:11435/v1"
export MODEL_NAME="llama3.2:3b"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export GRAPHITI_ENV="dev"

echo "Variables configuradas:"
echo "  OPENAI_API_KEY: $OPENAI_API_KEY"
echo "  OPENAI_BASE_URL: $OPENAI_BASE_URL"
echo "  MODEL_NAME: $MODEL_NAME"
echo "  NEO4J_URI: $NEO4J_URI"

# Verificar que Neo4j esté corriendo
echo ""
echo "Verificando Neo4j..."
if systemctl is-active --quiet neo4j; then
    echo "✓ Neo4j está activo"
else
    echo "⚠ Iniciando Neo4j..."
    systemctl start neo4j
    sleep 5
fi

# Verificar que el proxy de embeddings esté corriendo
echo ""
echo "Verificando proxy de embeddings..."
if curl -s http://localhost:11435/v1/models > /dev/null; then
    echo "✓ Proxy de embeddings está funcionando"
else
    echo "⚠ Iniciando proxy de embeddings..."
    nohup python3 /root/ollama_embeddings_proxy.py > /root/embeddings_proxy.log 2>&1 &
    sleep 3
    
    if curl -s http://localhost:11435/v1/models > /dev/null; then
        echo "✓ Proxy iniciado correctamente"
    else
        echo "✗ Error iniciando proxy"
        exit 1
    fi
fi

echo ""
echo "=== Configuración completada ==="
echo "Ahora puedes ejecutar Graphiti MCP con:"
echo "python3 /path/to/graphiti_mcp_server.py --transport sse --group-id test_integration"