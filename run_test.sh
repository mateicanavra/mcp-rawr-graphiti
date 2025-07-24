#!/bin/bash
# run_test.sh - Ejecutar suite completa de pruebas de integración

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"
START_TIME=$(date +%s)

echo -e "${BLUE}=== INICIANDO SUITE DE PRUEBAS DE INTEGRACIÓN OLLAMA + GRAPHITI ===${NC}"
echo "Fecha: $(date)"
echo "Log file: $LOG_FILE"
echo "============================================================================"

# Función para logging
log_and_echo() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Función para manejar errores
handle_error() {
    local exit_code=$1
    local operation=$2
    
    if [ $exit_code -ne 0 ]; then
        log_and_echo "${RED}❌ ERROR en: $operation${NC}"
        log_and_echo "${RED}   Código de salida: $exit_code${NC}"
        log_and_echo "${YELLOW}   Ver detalles en: $LOG_FILE${NC}"
        exit $exit_code
    else
        log_and_echo "${GREEN}✅ $operation: EXITOSO${NC}"
    fi
}

# 1. Verificar pre-requisitos
log_and_echo "\n${YELLOW}PASO 1: Verificando pre-requisitos...${NC}"
if ./check_prereqs.sh >> "$LOG_FILE" 2>&1; then
    handle_error 0 "Verificación de pre-requisitos"
else
    handle_error 1 "Verificación de pre-requisitos"
fi

# 2. Ejecutar prueba principal
log_and_echo "\n${YELLOW}PASO 2: Ejecutando test_integration.py...${NC}"
if python3 test_integration.py >> "$LOG_FILE" 2>&1; then
    handle_error 0 "Prueba de integración principal"
else
    handle_error 1 "Prueba de integración principal"
fi

# 3. Verificar resultados en el log
log_and_echo "\n${YELLOW}PASO 3: Analizando resultados...${NC}"

# Contar operaciones exitosas
OLLAMA_SUCCESS=$(grep -c "Respuesta:" "$LOG_FILE" || echo "0")
GRAPHITI_ACCEPTED=$(grep -c "Accepted" "$LOG_FILE" || echo "0")
ERRORS_FOUND=$(grep -c -E "(Error|FAIL|error)" "$LOG_FILE" || echo "0")

log_and_echo "   Consultas Ollama exitosas: $OLLAMA_SUCCESS"
log_and_echo "   Operaciones Graphiti aceptadas: $GRAPHITI_ACCEPTED"
log_and_echo "   Errores encontrados: $ERRORS_FOUND"

# 4. Verificar que la prueba se completó
if grep -q "PRUEBA COMPLETADA" "$LOG_FILE"; then
    log_and_echo "${GREEN}✅ La prueba se completó correctamente${NC}"
else
    log_and_echo "${RED}❌ La prueba no se completó${NC}"
    exit 1
fi

# 5. Calcular tiempo total
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_and_echo "\n${BLUE}Tiempo total de ejecución: ${DURATION} segundos${NC}"

# 6. Generar reporte final
log_and_echo "\n${YELLOW}PASO 4: Generando reporte final...${NC}"

REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# Reporte de Prueba de Integración Ollama + Graphiti

**Fecha:** $(date)  
**Duración Total:** ${DURATION} segundos  
**Log File:** $LOG_FILE  

## Componentes Verificados

- **Ollama (192.168.100.20:11434):** ✅ OK
- **Graphiti MCP (localhost:8000):** ✅ OK  
- **Modelo IA:** llama3.2:3b ✅ OK

## Operaciones Realizadas

- **Consultas Ollama exitosas:** $OLLAMA_SUCCESS
- **Operaciones Graphiti aceptadas:** $GRAPHITI_ACCEPTED
- **Errores encontrados:** $ERRORS_FOUND

## Métricas de Rendimiento

- **Tiempo total:** ${DURATION}s
- **Tiempo promedio por consulta:** $((OLLAMA_SUCCESS > 0 ? DURATION / OLLAMA_SUCCESS : 0))s

## Detalles de la Prueba

$(tail -n 20 "$LOG_FILE")

## Conclusión

EOF

if [ $ERRORS_FOUND -eq 0 ] && [ $OLLAMA_SUCCESS -gt 0 ] && [ $GRAPHITI_ACCEPTED -gt 0 ]; then
    echo "**RESULTADO: ✅ EXITOSA**" >> "$REPORT_FILE"
    log_and_echo "${GREEN}✅ TODAS LAS PRUEBAS EXITOSAS${NC}"
    FINAL_STATUS=0
else
    echo "**RESULTADO: ❌ FALLIDA**" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "### Errores Detectados:" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    grep -E "(Error|FAIL|error)" "$LOG_FILE" | head -10 >> "$REPORT_FILE" || echo "No se encontraron errores específicos en el log" >> "$REPORT_FILE"
    log_and_echo "${RED}❌ PRUEBAS FALLIDAS${NC}"
    FINAL_STATUS=1
fi

log_and_echo "\n${BLUE}Reporte generado: $REPORT_FILE${NC}"

# 7. Mostrar resumen
log_and_echo "\n============================================================================"
log_and_echo "${BLUE}RESUMEN FINAL:${NC}"
log_and_echo "   📊 Operaciones: $OLLAMA_SUCCESS consultas Ollama, $GRAPHITI_ACCEPTED ops Graphiti"
log_and_echo "   ⏱️  Duración: ${DURATION}s"
log_and_echo "   📝 Logs: $LOG_FILE"
log_and_echo "   📋 Reporte: $REPORT_FILE"

if [ $FINAL_STATUS -eq 0 ]; then
    log_and_echo "${GREEN}   🎉 ESTADO: TODAS LAS PRUEBAS EXITOSAS${NC}"
else
    log_and_echo "${RED}   🚨 ESTADO: PRUEBAS FALLIDAS${NC}"
fi

log_and_echo "============================================================================"

exit $FINAL_STATUS