#!/usr/bin/env python3
"""
Crear datos de ejemplo directamente en Neo4j para mostrar visualización de grafos
"""

from neo4j import GraphDatabase
from datetime import datetime
import uuid

# Configuración
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

def create_sample_data():
    """Crear datos de ejemplo en Neo4j"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            print("🧹 Limpiando datos existentes...")
            session.run("MATCH (n) DETACH DELETE n")
            
            print("📊 Creando datos de ejemplo...")
            
            # 1. Crear episodios (simulando conversaciones con Ollama)
            episode_queries = [
                """
                CREATE (e:EpisodicNode {
                    uuid: $uuid1,
                    name: 'Consulta sobre Tesla Roadster',
                    episode_body: 'Pregunta: ¿Qué sabes sobre el Tesla Roadster?\\n\\nRespuesta: El Tesla Roadster es un automóvil deportivo eléctrico producido por Tesla. La primera generación se lanzó en 2008 y fue el primer vehículo eléctrico de producción en utilizar celdas de batería de iones de litio.',
                    created_at: datetime(),
                    source_description: 'Respuesta de Ollama - llama3.2:3b',
                    group_id: 'test_integration'
                })
                """,
                """
                CREATE (e:EpisodicNode {
                    uuid: $uuid2,
                    name: 'Consulta sobre Neo4j',
                    episode_body: 'Pregunta: ¿Cuáles son las ventajas de Neo4j?\\n\\nRespuesta: Neo4j es una base de datos de grafos que ofrece ventajas como consultas eficientes de relaciones, flexibilidad de esquema, capacidad de manejar datos conectados complejos y un lenguaje de consulta intuitivo llamado Cypher.',
                    created_at: datetime(),
                    source_description: 'Respuesta de Ollama - llama3.2:3b',
                    group_id: 'test_integration'
                })
                """,
                """
                CREATE (e:EpisodicNode {
                    uuid: $uuid3,
                    name: 'Consulta sobre Grafos de Conocimiento',
                    episode_body: 'Pregunta: ¿Qué es un grafo de conocimiento?\\n\\nRespuesta: Un grafo de conocimiento es una representación estructurada de información que utiliza nodos para representar entidades y aristas para representar relaciones entre ellas. Permite organizar el conocimiento de manera que sea fácil de consultar y razonar.',
                    created_at: datetime(),
                    source_description: 'Respuesta de Ollama - llama3.2:3b',
                    group_id: 'test_integration'
                })
                """
            ]
            
            # Ejecutar creación de episodios
            for i, query in enumerate(episode_queries, 1):
                session.run(query, uuid1=str(uuid.uuid4()), uuid2=str(uuid.uuid4()), uuid3=str(uuid.uuid4()))
                print(f"   ✅ Episodio {i} creado")
            
            # 2. Crear entidades
            entity_queries = [
                """
                CREATE (t:Entity {
                    uuid: $uuid,
                    name: 'Tesla',
                    summary: 'Empresa de vehículos eléctricos fundada por Elon Musk',
                    labels: ['Company', 'Technology'],
                    created_at: datetime()
                })
                """,
                """
                CREATE (r:Entity {
                    uuid: $uuid,
                    name: 'Roadster',
                    summary: 'Automóvil deportivo eléctrico de Tesla',
                    labels: ['Product', 'Vehicle'],
                    created_at: datetime()
                })
                """,
                """
                CREATE (n:Entity {
                    uuid: $uuid,
                    name: 'Neo4j',
                    summary: 'Base de datos de grafos líder en la industria',
                    labels: ['Database', 'Technology'],
                    created_at: datetime()
                })
                """,
                """
                CREATE (kg:Entity {
                    uuid: $uuid,
                    name: 'Knowledge Graph',
                    summary: 'Estructura de datos que representa conocimiento mediante nodos y relaciones',
                    labels: ['Concept', 'Technology'],
                    created_at: datetime()
                })
                """,
                """
                CREATE (ai:Entity {
                    uuid: $uuid,
                    name: 'Artificial Intelligence',
                    summary: 'Campo de la informática que desarrolla sistemas inteligentes',
                    labels: ['Concept', 'Technology'],
                    created_at: datetime()
                })
                """,
                """
                CREATE (ollama:Entity {
                    uuid: $uuid,
                    name: 'Ollama',
                    summary: 'Plataforma para ejecutar modelos de lenguaje localmente',
                    labels: ['Software', 'AI'],
                    created_at: datetime()
                })
                """
            ]
            
            # Ejecutar creación de entidades
            for i, query in enumerate(entity_queries, 1):
                session.run(query, uuid=str(uuid.uuid4()))
                print(f"   ✅ Entidad {i} creada")
            
            # 3. Crear relaciones entre entidades
            relationship_queries = [
                "MATCH (t:Entity {name: 'Tesla'}), (r:Entity {name: 'Roadster'}) CREATE (t)-[:MANUFACTURES {since: '2008'}]->(r)",
                "MATCH (kg:Entity {name: 'Knowledge Graph'}), (n:Entity {name: 'Neo4j'}) CREATE (kg)-[:STORED_IN {efficiency: 'high'}]->(n)",
                "MATCH (ai:Entity {name: 'Artificial Intelligence'}), (kg:Entity {name: 'Knowledge Graph'}) CREATE (ai)-[:USES {purpose: 'memory'}]->(kg)",
                "MATCH (ollama:Entity {name: 'Ollama'}), (ai:Entity {name: 'Artificial Intelligence'}) CREATE (ollama)-[:PROVIDES {type: 'language_models'}]->(ai)",
                "MATCH (t:Entity {name: 'Tesla'}), (ai:Entity {name: 'Artificial Intelligence'}) CREATE (t)-[:DEVELOPS {focus: 'autonomous_driving'}]->(ai)",
                "MATCH (n:Entity {name: 'Neo4j'}), (kg:Entity {name: 'Knowledge Graph'}) CREATE (n)-[:SPECIALIZES_IN]->(kg)"
            ]
            
            # Ejecutar creación de relaciones
            for i, query in enumerate(relationship_queries, 1):
                session.run(query)
                print(f"   ✅ Relación {i} creada")
            
            # 4. Conectar episodios con entidades mencionadas
            mention_queries = [
                "MATCH (e:EpisodicNode {name: 'Consulta sobre Tesla Roadster'}), (t:Entity {name: 'Tesla'}) CREATE (e)-[:MENTIONS]->(t)",
                "MATCH (e:EpisodicNode {name: 'Consulta sobre Tesla Roadster'}), (r:Entity {name: 'Roadster'}) CREATE (e)-[:MENTIONS]->(r)",
                "MATCH (e:EpisodicNode {name: 'Consulta sobre Neo4j'}), (n:Entity {name: 'Neo4j'}) CREATE (e)-[:MENTIONS]->(n)",
                "MATCH (e:EpisodicNode {name: 'Consulta sobre Grafos de Conocimiento'}), (kg:Entity {name: 'Knowledge Graph'}) CREATE (e)-[:MENTIONS]->(kg)",
                "MATCH (e:EpisodicNode), (ollama:Entity {name: 'Ollama'}) CREATE (e)-[:GENERATED_BY]->(ollama)"
            ]
            
            # Ejecutar menciones
            for i, query in enumerate(mention_queries, 1):
                session.run(query)
                print(f"   ✅ Mención {i} creada")
            
            print("\n📊 Verificando datos creados...")
            
            # Verificar creación
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = result.single()["total_nodes"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
            total_rels = result.single()["total_relationships"]
            
            print(f"   ✅ {total_nodes} nodos creados")
            print(f"   ✅ {total_rels} relaciones creadas")
            
    finally:
        driver.close()

def print_instructions():
    """Imprimir instrucciones para usar Neo4j Browser"""
    print("\n🌐 CÓMO VER LOS GRAFOS EN NEO4J BROWSER")
    print("=" * 50)
    print("1. Abrir en navegador: http://localhost:7474")
    print("2. Conectar con:")
    print("   • Usuario: neo4j")
    print("   • Password: admin123")
    print("3. Probar estos queries:")
    print()
    
    queries = [
        ("Ver todo el grafo", "MATCH (n)-[r]-(m) RETURN n, r, m"),
        ("Ver solo episodios", "MATCH (e:EpisodicNode) RETURN e"),
        ("Ver solo entidades", "MATCH (e:Entity) RETURN e"),
        ("Ver Tesla y sus relaciones", "MATCH (t:Entity {name: 'Tesla'})-[r]-(connected) RETURN t, r, connected"),
        ("Ver estructura completa", "MATCH (n) RETURN n LIMIT 25")
    ]
    
    for i, (desc, query) in enumerate(queries, 1):
        print(f"{i}. {desc}:")
        print(f"   {query}")
        print()
    
    print("💡 Tips:")
    print("   • Los nodos aparecerán como círculos de colores")
    print("   • Las relaciones aparecerán como líneas con etiquetas")
    print("   • Hacer click en nodos para ver propiedades")
    print("   • Usar zoom y drag para navegar")

if __name__ == "__main__":
    print("🎯 CREANDO DATOS DE EJEMPLO PARA VISUALIZACIÓN")
    print(f"Fecha: {datetime.now()}")
    print("=" * 60)
    
    try:
        create_sample_data()
        print_instructions()
        
        print(f"\n✅ DATOS CREADOS EXITOSAMENTE")
        print(f"🌐 Abrir Neo4j Browser: http://localhost:7474")
        
    except Exception as e:
        print(f"❌ Error: {e}")