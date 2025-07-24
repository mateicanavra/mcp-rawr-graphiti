#!/bin/bash
# setup_visualizer.sh - Configurar y ejecutar el visualizador web

echo "🚀 Configurando Visualizador Web de Graphiti"
echo "============================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Verificar Python
echo -e "${YELLOW}1. Verificando Python...${NC}"
if python3 --version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python disponible: $(python3 --version)${NC}"
else
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi

# 2. Instalar dependencias
echo -e "${YELLOW}2. Instalando dependencias...${NC}"
pip3 install fastapi uvicorn neo4j requests jinja2 python-multipart aiofiles

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias${NC}"
    exit 1
fi

# 3. Verificar configuración
echo -e "${YELLOW}3. Verificando configuración...${NC}"

# Verificar Neo4j
if curl -f -s http://localhost:7474 > /dev/null; then
    echo -e "${GREEN}✅ Neo4j disponible en puerto 7474${NC}"
else
    echo -e "${RED}❌ Neo4j no disponible en puerto 7474${NC}"
    echo "   Ejecutar: docker-compose up -d neo4j"
fi

# Verificar Graphiti MCP
if curl -f -s http://localhost:8000/sse > /dev/null; then
    echo -e "${GREEN}✅ Graphiti MCP disponible en puerto 8000${NC}"
else
    echo -e "${RED}❌ Graphiti MCP no disponible en puerto 8000${NC}"
    echo "   Ejecutar: docker-compose up -d"
fi

# 4. Configurar variables de entorno
echo -e "${YELLOW}4. Configurando variables de entorno...${NC}"

# Leer del .env si existe
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✅ Variables cargadas desde .env${NC}"
else
    echo -e "${YELLOW}⚠️  No se encontró .env, usando valores por defecto${NC}"
    export NEO4J_URI="bolt://localhost:7687"
    export NEO4J_USER="neo4j"
    export NEO4J_PASSWORD="admin123"
fi

echo "   NEO4J_URI: ${NEO4J_URI:-bolt://localhost:7687}"
echo "   NEO4J_USER: ${NEO4J_USER:-neo4j}"
echo "   GRAPHITI_MCP_URL: ${GRAPHITI_MCP_URL:-http://localhost:8000}"

# 5. Crear archivo de inicio
echo -e "${YELLOW}5. Creando script de inicio...${NC}"

cat > start_visualizer.sh << 'EOF'
#!/bin/bash
# Cargar variables de entorno
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Valores por defecto
export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-admin123}"
export GRAPHITI_MCP_URL="${GRAPHITI_MCP_URL:-http://localhost:8000}"

echo "🌐 Iniciando Visualizador Web..."
echo "   Neo4j: $NEO4J_URI"
echo "   Graphiti: $GRAPHITI_MCP_URL"
echo "   Web: http://localhost:8080"
echo ""

python3 web_visualizer.py
EOF

chmod +x start_visualizer.sh

echo -e "${GREEN}✅ Script de inicio creado: start_visualizer.sh${NC}"

# 6. Instrucciones finales
echo ""
echo -e "${YELLOW}============================================${NC}"
echo -e "${GREEN}🎉 CONFIGURACIÓN COMPLETADA${NC}"
echo ""
echo -e "${YELLOW}Para ejecutar el visualizador:${NC}"
echo "   ./start_visualizer.sh"
echo ""
echo -e "${YELLOW}O directamente:${NC}"
echo "   python3 web_visualizer.py"
echo ""
echo -e "${YELLOW}Una vez iniciado, abrir en navegador:${NC}"
echo "   http://localhost:8080"
echo ""
echo -e "${YELLOW}Opciones de visualización:${NC}"
echo "   • Neo4j Browser: http://localhost:7474"
echo "   • Visualizador Custom: http://localhost:8080"
echo ""
echo -e "${YELLOW}============================================${NC}"