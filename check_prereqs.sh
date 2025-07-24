#!/bin/bash
# check_prereqs.sh - Verificar pre-requisitos para pruebas de integración

set -e

echo "=== VERIFICANDO PRE-REQUISITOS PARA INTEGRACIÓN OLLAMA + GRAPHITI ==="
echo "Fecha: $(date)"
echo "============================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error_count=0

# Función para mostrar resultado
show_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2: OK${NC}"
    else
        echo -e "${RED}❌ $2: FAIL${NC}"
        ((error_count++))
    fi
}

# 1. Verificar conectividad con Ollama
echo -e "\n${YELLOW}1. Verificando Ollama en VM (192.168.100.20:11434)...${NC}"

if curl -f -s http://192.168.100.20:11434/api/tags > /dev/null 2>&1; then
    show_result 0 "Conexión Ollama"
    
    # Verificar modelo específico
    if curl -s http://192.168.100.20:11434/api/tags | grep -q "llama3.2:3b"; then
        show_result 0 "Modelo llama3.2:3b disponible"
    else
        show_result 1 "Modelo llama3.2:3b disponible"
        echo -e "${YELLOW}   Modelos disponibles:${NC}"
        curl -s http://192.168.100.20:11434/api/tags | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g' | sed 's/^/   - /'
    fi
else
    show_result 1 "Conexión Ollama"
    echo "   Error: No se puede conectar con http://192.168.100.20:11434"
fi

# 2. Verificar Graphiti MCP Server
echo -e "\n${YELLOW}2. Verificando Graphiti MCP Server (localhost:8000)...${NC}"

if curl -f -s http://localhost:8000/sse > /dev/null 2>&1; then
    show_result 0 "Servidor Graphiti"
    
    # Obtener Session ID
    SESSION_RESPONSE=$(curl -s http://localhost:8000/sse)
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o 'session_id=[^"]*' | cut -d= -f2 || true)
    
    if [ ! -z "$SESSION_ID" ]; then
        show_result 0 "Session ID obtenido"
        echo -e "${GREEN}   Session ID: $SESSION_ID${NC}"
        
        # Actualizar el script de prueba con el nuevo Session ID
        if [ -f "test_integration.py" ]; then
            if sed -i.bak "s/SESSION_ID = \".*\"/SESSION_ID = \"$SESSION_ID\"/" test_integration.py 2>/dev/null; then
                show_result 0 "Script actualizado con nueva sesión"
            else
                # Para macOS, usar una sintaxis diferente
                sed -i '' "s/SESSION_ID = \".*\"/SESSION_ID = \"$SESSION_ID\"/" test_integration.py
                show_result 0 "Script actualizado con nueva sesión (macOS)"
            fi
        else
            show_result 1 "Script test_integration.py no encontrado"
        fi
    else
        show_result 1 "Session ID obtenido"
        echo "   Error: No se pudo extraer Session ID de la respuesta"
    fi
else
    show_result 1 "Servidor Graphiti"
    echo "   Error: No se puede conectar con http://localhost:8000"
fi

# 3. Verificar dependencias de Python
echo -e "\n${YELLOW}3. Verificando dependencias de Python...${NC}"

if python3 -c "import requests" 2>/dev/null; then
    show_result 0 "Módulo requests"
else
    show_result 1 "Módulo requests"
    echo "   Instalar con: pip install requests"
fi

if python3 -c "import json" 2>/dev/null; then
    show_result 0 "Módulo json"
else
    show_result 1 "Módulo json"
fi

# 4. Verificar archivos necesarios
echo -e "\n${YELLOW}4. Verificando archivos de prueba...${NC}"

if [ -f "test_integration.py" ]; then
    show_result 0 "Script test_integration.py"
else
    show_result 1 "Script test_integration.py"
fi

if [ -f "README_test_integration.md" ]; then
    show_result 0 "Documentación README"
else
    show_result 1 "Documentación README"
fi

# 5. Prueba rápida de conectividad
echo -e "\n${YELLOW}5. Realizando pruebas rápidas de conectividad...${NC}"

# Prueba rápida Ollama
echo -n "   Probando Ollama con query simple... "
OLLAMA_TEST=$(curl -s -X POST "http://192.168.100.20:11434/api/generate" \
    -H "Content-Type: application/json" \
    -d '{"model": "llama3.2:3b", "prompt": "Hola", "stream": false}' \
    --max-time 30 2>/dev/null || echo "ERROR")

if echo "$OLLAMA_TEST" | grep -q '"response"'; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    ((error_count++))
fi

# Prueba rápida Graphiti (solo si tenemos session ID)
if [ ! -z "$SESSION_ID" ]; then
    echo -n "   Probando Graphiti con query simple... "
    GRAPHITI_TEST=$(curl -s -X POST "http://localhost:8000/messages/?session_id=$SESSION_ID" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc": "2.0", "method": "resource", "params": {"uri": "http://graphiti/status"}, "id": 1}' \
        --max-time 10 2>/dev/null || echo "ERROR")
    
    if echo "$GRAPHITI_TEST" | grep -q -E "(Accepted|ok)" || [ ${#GRAPHITI_TEST} -gt 5 ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}"
        ((error_count++))
    fi
else
    echo -e "   ${YELLOW}Saltando prueba Graphiti (no hay Session ID)${NC}"
fi

# Resumen final
echo -e "\n============================================================================"
if [ $error_count -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS LOS PRE-REQUISITOS OK - LISTO PARA EJECUTAR PRUEBAS${NC}"
    echo -e "${GREEN}   Ejecutar: python3 test_integration.py${NC}"
    exit 0
else
    echo -e "${RED}❌ ENCONTRADOS $error_count ERRORES - CORREGIR ANTES DE EJECUTAR PRUEBAS${NC}"
    echo -e "${YELLOW}   Revisar la configuración de los componentes fallidos${NC}"
    exit 1
fi