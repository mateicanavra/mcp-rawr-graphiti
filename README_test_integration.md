# Guía de Integración Ollama + Graphiti

Esta guía documenta el script `test_integration.py` que demuestra la integración entre el sistema de IA Ollama (ejecutándose en VM) y el servidor MCP de Graphiti.

## 📋 Resumen de la Integración

El script realiza las siguientes operaciones:
1. **Conecta con Ollama** en la VM `192.168.100.20:11434`
2. **Hace preguntas** al modelo `llama3.2:3b`
3. **Guarda las respuestas** como episodios en Graphiti
4. **Busca información** en el grafo de conocimiento de Graphiti

## 🛠️ Componentes del Sistema

### Ollama (VM: 192.168.100.20)
- **Puerto**: 11434
- **Modelo**: llama3.2:3b
- **Endpoint**: `/api/generate`
- **Función**: Procesamiento de lenguaje natural

### Graphiti MCP Server (Local)
- **Puerto**: 8000
- **Endpoint**: `/messages/`
- **Función**: Gestión de memoria en grafo de conocimiento
- **Protocolo**: Model Context Protocol (MCP)

## 📁 Estructura del Script

### Configuración
```python
OLLAMA_URL = "http://192.168.100.20:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
GRAPHITI_MCP_URL = "http://localhost:8000/messages/"
SESSION_ID = "5b6d90707c01457593e5610fc2129c66"
```

### Funciones Principales

#### `ask_ollama(prompt: str) -> str`
- Envía prompts al modelo de IA en la VM
- Maneja timeouts y errores de conexión
- Retorna la respuesta generada por el modelo

#### `add_episode_to_graphiti(name, content, group_id)`
- Crea episodios en el grafo de conocimiento
- Usa protocolo MCP para comunicarse con Graphiti
- Organiza información por `group_id`

#### `search_in_graphiti(query, group_id)`
- Busca nodos relacionados en el grafo
- Usa búsqueda semántica
- Filtra por grupos de información

## 🚀 Flujo de Ejecución

1. **Verificación de Conexiones**
   - Prueba conexión con Ollama
   - Verifica disponibilidad de Graphiti MCP

2. **Generación de Contenido**
   - Envía pregunta a Ollama: "¿Qué es un sistema de grafos de conocimiento?"
   - Recibe respuesta del modelo IA

3. **Almacenamiento en Graphiti**
   - Crea episodio con pregunta y respuesta
   - Asigna timestamp y metadatos
   - Guarda en grupo `test_integration`

4. **Procesamiento**
   - Espera 10 segundos para procesamiento asíncrono
   - Permite que Graphiti construya el grafo

5. **Búsqueda y Validación**
   - Busca términos relacionados: "grafos conocimiento"
   - Verifica que la información esté indexada

6. **Segunda Iteración**
   - Pregunta específica sobre Neo4j
   - Repite el ciclo de almacenamiento

## 📊 Resultados Esperados

### Exitoso ✅
```
Resultado de Graphiti: Accepted
Búsqueda 'grafos conocimiento': Accepted
```

### Con Errores ❌
```
Could not find session
Error al llamar a Ollama: [detalles]
Error al conectar con Graphiti: [detalles]
```

## 🔧 Requisitos Previos

### VM Ollama (192.168.100.20)
- [x] Servidor Ollama corriendo en puerto 11434
- [x] Modelo `llama3.2:3b` descargado
- [x] Acceso de red desde la máquina local

### Local Graphiti
- [x] Servidor MCP corriendo en puerto 8000
- [x] Base de datos Neo4j configurada
- [x] Sesión válida obtenida desde `/sse`

### Python Dependencies
```bash
pip install requests
```

## 📝 Logs de Ejemplo

```
=== PRUEBA DE INTEGRACIÓN OLLAMA + GRAPHITI ===
Fecha: 2025-07-23 20:26:15.053001
Ollama URL: http://192.168.100.20:11434/api/generate
Modelo: llama3.2:3b
Graphiti MCP URL: http://localhost:8000/messages/

1. Probando conexión con Ollama...
Pregunta: ¿Qué es un sistema de grafos de conocimiento?
Respuesta: ¡Excelente pregunta! Un sistema de grafos de conocimiento...

2. Guardando respuesta en Graphiti...
Resultado de Graphiti: Accepted

3. Esperando procesamiento...

4. Buscando en Graphiti...
Búsqueda 'grafos conocimiento': Accepted

5. Segunda prueba con pregunta específica...
Pregunta específica: ¿Cuáles son las ventajas de usar Neo4j...
Respuesta: **Ventajas de usar Neo4j para almacenar grafos de conocimiento**...
Segundo episodio guardado: Accepted

=== PRUEBA COMPLETADA ===
```

## 🎯 Casos de Uso

### 1. Investigación Asistida por IA
- Hacer preguntas complejas a Ollama
- Almacenar respuestas estructuradas en Graphiti
- Buscar información relacionada posteriormente

### 2. Construcción de Base de Conocimiento
- Generar contenido sobre temas específicos
- Crear redes de conceptos interconectados
- Facilitar descubrimiento de relaciones

### 3. Sistema de Memoria Persistente
- Mantener historial de consultas
- Evolucionar conocimiento a través del tiempo
- Recuperar contexto de conversaciones previas

## 🔍 Verificación Manual

### Comprobar Ollama
```bash
curl -X GET "http://192.168.100.20:11434/api/tags"
```

### Obtener Nueva Sesión Graphiti
```bash
curl http://localhost:8000/sse
```

### Verificar Estado del Servidor
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<ID>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "resource", "params": {"uri": "http://graphiti/status"}, "id": 1}'
```

## 📈 Métricas de Rendimiento

| Operación | Tiempo Promedio | Timeout |
|-----------|----------------|---------|
| Consulta Ollama | 30-60 segundos | 90s |
| Add Episode | <1 segundo | 30s |
| Search Nodes | <1 segundo | 30s |
| Procesamiento BG | 5-15 segundos | N/A |

## 🚨 Troubleshooting

### Error: "Could not find session"
- Obtener nueva sesión desde `/sse`
- Actualizar `SESSION_ID` en el script

### Error: "model 'X' not found"
- Verificar modelos disponibles en Ollama
- Descargar modelo requerido: `ollama pull llama3.2:3b`

### Timeout en Ollama
- Verificar conectividad de red con la VM
- Aumentar timeout en la función `ask_ollama`

### "Accepted" sin resultados
- Normal - Graphiti procesa episodios asíncronamente
- Esperar más tiempo antes de buscar
- Verificar logs del servidor Graphiti