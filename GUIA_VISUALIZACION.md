# 🕸️ Guía de Visualización de Grafos Graphiti

## 🎯 Opciones Disponibles

### 1. 🚀 Neo4j Browser (Más Rápida)
- **URL**: http://localhost:7474
- **Usuario**: neo4j  
- **Password**: admin123
- **Ventajas**: Nativa, potente, muchas opciones de query
- **Para usar**: Simplemente abrir en navegador y conectar

### 2. 🎨 Visualizador Web Custom (Más Amigable)
- **URL**: http://localhost:8080
- **Ventajas**: Interfaz amigable, integración con Graphiti MCP
- **Para usar**: Ejecutar `./setup_visualizer.sh` y luego `./start_visualizer.sh`

## 🔧 Setup Rápido

### Opción A: Neo4j Browser
```bash
# 1. Verificar que Neo4j esté corriendo
curl http://localhost:7474

# 2. Abrir en navegador
open http://localhost:7474

# 3. Conectar con:
# - URI: bolt://localhost:7687
# - Usuario: neo4j
# - Password: admin123
```

### Opción B: Visualizador Custom
```bash
# 1. Configurar e instalar
./setup_visualizer.sh

# 2. Ejecutar visualizador
./start_visualizer.sh

# 3. Abrir en navegador
open http://localhost:8080
```

## 📊 Queries Útiles para Neo4j Browser

### Ver todos los nodos
```cypher
MATCH (n) RETURN n LIMIT 25
```

### Ver episodios recientes
```cypher
MATCH (e:EpisodicNode) 
RETURN e.name, e.episode_body, e.created_at 
ORDER BY e.created_at DESC 
LIMIT 10
```

### Ver relaciones entre entidades
```cypher
MATCH (a)-[r]->(b) 
RETURN a.name, type(r), b.name 
LIMIT 20
```

### Buscar por contenido específico
```cypher
MATCH (n) 
WHERE n.name CONTAINS "Tesla" 
   OR n.summary CONTAINS "Tesla"
   OR n.episode_body CONTAINS "Tesla"
RETURN n
```

### Ver estructura del grafo
```cypher
CALL db.schema.visualization()
```

### Estadísticas del grafo
```cypher
MATCH (n) 
RETURN labels(n) as NodeType, count(n) as Count
```

## 🎨 Funcionalidades del Visualizador Custom

### Pantalla Principal
- **Estadísticas**: Nodos, relaciones, episodios
- **Controles**: Cargar, buscar, limpiar
- **Visualización D3.js**: Interactiva y con drag&drop

### Botones Disponibles
- 🔄 **Cargar Grafo**: Carga nodos y relaciones desde Neo4j
- 📄 **Ver Episodios**: Muestra episodios recientes desde Graphiti MCP  
- 🔍 **Buscar**: Busca nodos por contenido
- 🧹 **Limpiar**: Limpia la visualización

### Interactividad
- **Click en nodos**: Muestra información detallada
- **Drag & drop**: Reorganizar el grafo
- **Hover**: Destacar nodos
- **Zoom**: Navegación en el grafo

## 📈 Datos que Verás

### Después de ejecutar test_integration.py
- **Episodios**: Preguntas y respuestas de Ollama
- **Entidades**: Tesla, Roadster, Neo4j, etc.
- **Relaciones**: Conexiones semánticas entre conceptos

### Tipos de Nodos
- **EpisodicNode**: Episodios de conversación
- **Entity**: Entidades extraídas (empresas, productos, conceptos)
- **Fact**: Relaciones/hechos entre entidades

### Tipos de Relaciones
- **RELATES_TO**: Relación general entre entidades
- **MENTIONED_IN**: Entidad mencionada en episodio
- **SIMILAR_TO**: Entidades similares

## 🔍 Ejemplos de Búsqueda

### En Neo4j Browser
```cypher
// Buscar todo relacionado con Tesla
MATCH (n)-[r]-(m) 
WHERE n.name CONTAINS "Tesla" 
RETURN n, r, m

// Ver episodios de Ollama
MATCH (e:EpisodicNode) 
WHERE e.source_description CONTAINS "Ollama"
RETURN e.name, e.created_at

// Encontrar entidades más conectadas
MATCH (n)-[r]-() 
RETURN n.name, count(r) as connections 
ORDER BY connections DESC 
LIMIT 10
```

### En Visualizador Custom
- Escribir "Tesla" en el campo de búsqueda
- Hacer click en "🔍 Buscar"
- Ver resultados en panel de información

## 🚨 Troubleshooting

### Error: No se puede conectar a Neo4j
```bash
# Verificar que esté corriendo
docker ps | grep neo4j

# Si no está corriendo
docker-compose up -d neo4j

# Verificar puerto
curl http://localhost:7474
```

### Error: No se puede conectar a Graphiti MCP
```bash
# Verificar servidor
curl http://localhost:8000/sse

# Si no responde
docker-compose up -d graphiti-mcp-root
```

### Error: Dependencias faltantes
```bash
# Reinstalar dependencias
pip3 install fastapi uvicorn neo4j requests jinja2

# O usar el setup
./setup_visualizer.sh
```

### Grafo vacío
```bash
# Ejecutar pruebas primero para generar datos
python3 test_integration.py

# Luego cargar visualizador
./start_visualizer.sh
```

## 🎯 Casos de Uso

### 1. Exploración de Conocimiento
- Ver cómo se conectan conceptos
- Descubrir relaciones no obvias
- Analizar la estructura del conocimiento almacenado

### 2. Debugging de Graphiti
- Verificar que los episodios se guardaron correctamente
- Ver qué entidades se extrajeron
- Analizar la calidad de las relaciones

### 3. Análisis de Conversaciones
- Ver el historial de preguntas a Ollama
- Analizar temas recurrentes
- Identificar gaps en el conocimiento

### 4. Demostración
- Mostrar visualmente cómo funciona Graphiti
- Explicar conceptos de grafos de conocimiento
- Demostrar capacidades del sistema

## 📊 Comparación de Opciones

| Característica | Neo4j Browser | Visualizador Custom |
|----------------|---------------|-------------------|
| **Velocidad** | ⚡⚡⚡ Muy rápida | ⚡⚡ Rápida |
| **Funcionalidad** | ⭐⭐⭐⭐⭐ Completa | ⭐⭐⭐ Buena |
| **Facilidad de uso** | ⭐⭐⭐ Media | ⭐⭐⭐⭐⭐ Muy fácil |
| **Queries** | ⭐⭐⭐⭐⭐ Cypher completo | ⭐⭐ Limitadas |
| **Integración MCP** | ❌ No | ✅ Sí |
| **Personalización** | ⭐⭐ Limitada | ⭐⭐⭐⭐ Alta |

## 🎉 Recomendación

### Para Desarrollo/Debug: **Neo4j Browser**
- Más potente para análisis profundo
- Queries Cypher completas
- Herramientas avanzadas

### Para Demos/Presentaciones: **Visualizador Custom**  
- Interfaz más amigable
- Integración con Graphiti MCP
- Mejor para usuarios no técnicos

---

## 🚀 ¡Empezar Ahora!

```bash
# Opción rápida - Neo4j Browser
open http://localhost:7474

# Opción completa - Visualizador Custom
./setup_visualizer.sh && ./start_visualizer.sh
```