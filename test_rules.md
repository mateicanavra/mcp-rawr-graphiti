# Reglas para Pruebas de Integración Ollama + Graphiti

## 🎯 Objetivos de las Pruebas

1. **Verificar conectividad** entre componentes
2. **Validar flujo de datos** desde Ollama hacia Graphiti
3. **Confirmar almacenamiento** y recuperación de información
4. **Medir rendimiento** de las operaciones

## 📋 Pre-requisitos Obligatorios

### Antes de ejecutar cualquier prueba:

#### ✅ Checklist de VM Ollama
```bash
# Verificar que Ollama esté corriendo
curl -f http://192.168.100.20:11434/api/tags > /dev/null
echo "Status: $?"  # Debe ser 0

# Verificar modelo disponible
curl -s http://192.168.100.20:11434/api/tags | grep -q "llama3.2:3b"
echo "Modelo disponible: $?"  # Debe ser 0
```

#### ✅ Checklist de Graphiti MCP
```bash
# Verificar servidor corriendo
curl -f http://localhost:8000/sse > /dev/null
echo "Status: $?"  # Debe ser 0

# Obtener sesión válida
SESSION_ID=$(curl -s http://localhost:8000/sse | grep "session_id=" | sed 's/.*session_id=\([^"]*\).*/\1/')
echo "Session ID: $SESSION_ID"  # No debe estar vacío
```

#### ✅ Checklist de Python
```bash
# Verificar dependencias
python3 -c "import requests; print('requests: OK')"
python3 -c "import json; print('json: OK')"
```

## 🔄 Protocolo de Pruebas

### Regla 1: Orden de Ejecución
```
1. Verificar pre-requisitos
2. Actualizar SESSION_ID en el script
3. Ejecutar test_integration.py
4. Validar resultados
5. Limpiar datos de prueba (opcional)
```

### Regla 2: Validación de Respuestas

#### Ollama Response ✅
- Debe contener texto coherente (> 50 caracteres)
- No debe contener mensajes de error
- Tiempo de respuesta < 90 segundos

#### Graphiti Response ✅
- Status debe ser "Accepted"
- No debe retornar "Could not find session"
- No debe retornar errores HTTP

### Regla 3: Tiempos de Espera

| Operación | Timeout Mínimo | Timeout Máximo |
|-----------|---------------|---------------|
| Ollama Query | 30s | 90s |
| Graphiti Add | 5s | 30s |
| Graphiti Search | 5s | 30s |
| Procesamiento BG | 10s | 60s |

### Regla 4: Manejo de Errores

#### Errores Recuperables (Reintentar)
- Timeout de red
- "Could not find session" (obtener nueva sesión)
- Respuesta vacía de Ollama

#### Errores Críticos (Detener prueba)
- Modelo no encontrado en Ollama
- Servidor Graphiti no responde
- Error de autenticación

## 🧪 Tipos de Pruebas

### 1. Prueba Básica (test_integration.py)
```python
# Preguntas simples para verificar conectividad
prompts = [
    "¿Qué es un grafo de conocimiento?",
    "¿Cuáles son las ventajas de Neo4j?"
]
```

### 2. Prueba de Carga
```python
# 10 preguntas consecutivas
for i in range(10):
    prompt = f"Pregunta número {i}: Explica conceptos de IA"
    # Procesar y almacenar
```

### 3. Prueba de Recuperación
```python
# Agregar datos conocidos y buscarlos
test_data = "Tesla Roadster es un auto eléctrico"
# Agregar a Graphiti
# Buscar "Tesla" y verificar resultado
```

### 4. Prueba de Rendimiento
```python
import time
start = time.time()
# Ejecutar operaciones
duration = time.time() - start
assert duration < MAX_TIME
```

## 📊 Criterios de Éxito

### Prueba EXITOSA ✅
- [x] Ollama responde coherentemente
- [x] Graphiti acepta episodios ("Accepted")
- [x] No hay errores de conexión
- [x] Tiempo total < 2 minutos

### Prueba FALLIDA ❌
- [ ] Error de conexión persistente
- [ ] Respuestas vacías o incoherentes
- [ ] Timeouts recurrentes
- [ ] Errores de sesión no recuperables

## 🔧 Scripts de Automatización

### Verificar Pre-requisitos
```bash
#!/bin/bash
# check_prereqs.sh

echo "=== Verificando Pre-requisitos ==="

# Ollama
if curl -f http://192.168.100.20:11434/api/tags &>/dev/null; then
    echo "✅ Ollama: OK"
else
    echo "❌ Ollama: FAIL"
    exit 1
fi

# Graphiti
if curl -f http://localhost:8000/sse &>/dev/null; then
    echo "✅ Graphiti: OK"
else
    echo "❌ Graphiti: FAIL"
    exit 1
fi

# Session ID
SESSION_ID=$(curl -s http://localhost:8000/sse | grep -o 'session_id=[^"]*' | cut -d= -f2)
if [ ! -z "$SESSION_ID" ]; then
    echo "✅ Session ID: $SESSION_ID"
    # Actualizar en el script
    sed -i '' "s/SESSION_ID = \".*\"/SESSION_ID = \"$SESSION_ID\"/" test_integration.py
else
    echo "❌ Session ID: FAIL"
    exit 1
fi

echo "✅ Todos los pre-requisitos OK"
```

### Ejecutar Prueba Completa
```bash
#!/bin/bash
# run_test.sh

set -e  # Salir en caso de error

echo "=== INICIANDO PRUEBAS DE INTEGRACIÓN ==="

# 1. Verificar pre-requisitos
./check_prereqs.sh

# 2. Ejecutar prueba principal
echo "=== Ejecutando test_integration.py ==="
python3 test_integration.py > test_results.log 2>&1

# 3. Verificar resultados
if grep -q "PRUEBA COMPLETADA" test_results.log && ! grep -q "Error\|FAIL" test_results.log; then
    echo "✅ PRUEBA EXITOSA"
    exit 0
else
    echo "❌ PRUEBA FALLIDA"
    echo "Ver detalles en test_results.log"
    exit 1
fi
```

## 📈 Monitoreo y Logs

### Logs Obligatorios
```python
# En cada función:
print(f"[{datetime.now()}] Iniciando operación: {operation_name}")
print(f"[{datetime.now()}] Resultado: {result}")
print(f"[{datetime.now()}] Tiempo transcurrido: {duration}s")
```

### Métricas a Registrar
- Tiempo de respuesta de Ollama
- Tiempo de procesamiento en Graphiti
- Número de episodios creados
- Número de búsquedas exitosas
- Errores encontrados

## 🚨 Alertas y Notificaciones

### Condiciones de Alerta
- Tiempo de respuesta > 90 segundos
- Error rate > 10%
- Servidor no disponible > 30 segundos

### Acciones de Recuperación
1. **Timeout Ollama**: Reintentar con timeout mayor
2. **Session Expired**: Obtener nueva sesión automáticamente
3. **Network Error**: Esperar 30s y reintentar

## 📝 Plantilla de Reporte

```
=== REPORTE DE PRUEBA ===
Fecha: [YYYY-MM-DD HH:MM:SS]
Duración Total: [XX segundos]

Componentes:
- Ollama (192.168.100.20:11434): [OK/FAIL]
- Graphiti (localhost:8000): [OK/FAIL]
- Modelo IA: llama3.2:3b [OK/FAIL]

Operaciones Realizadas:
- Consultas Ollama: [X exitosas / Y fallidas]
- Episodios Graphiti: [X creados / Y fallidos]
- Búsquedas: [X exitosas / Y fallidas]

Errores Encontrados:
[Lista de errores con timestamp]

Métricas de Rendimiento:
- Tiempo promedio Ollama: [XX]s
- Tiempo promedio Graphiti: [XX]s

Conclusión: [EXITOSA/FALLIDA]
```

## 🔄 Automatización CI/CD

### GitHub Actions / Jenkins
```yaml
name: Test Ollama-Graphiti Integration
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas

jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check Prerequisites
        run: ./check_prereqs.sh
      - name: Run Integration Test
        run: ./run_test.sh
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_results.log
```

Esta estructura de reglas asegura que las pruebas sean:
- **Consistentes**: Mismo proceso cada vez
- **Confiables**: Verificación de pre-requisitos
- **Trazables**: Logs detallados
- **Automatizables**: Scripts para CI/CD