#!/usr/bin/env python3
"""
Crear nodos de generación musical directamente en Neo4j
"""

from neo4j import GraphDatabase
from datetime import datetime
import uuid
import json

# Configuración Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

def create_musical_knowledge_graph():
    """Crear grafo de conocimiento musical en Neo4j"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            print("🎵 Creando grafo de conocimiento musical...")
            
            # Limpiar datos musicales existentes
            print("🧹 Limpiando datos musicales previos...")
            session.run("""
                MATCH (n) 
                WHERE n.domain = 'music' OR n.group_id = 'musical_generation'
                DETACH DELETE n
            """)
            
            # 1. Crear nodo principal de Generación Musical
            print("🎯 Creando nodo principal: Generación Musical")
            session.run("""
                CREATE (gm:Entity:MusicConcept {
                    uuid: $uuid,
                    name: 'Generación Musical',
                    summary: 'Sistema de IA para generar música usando teoría musical y modelos de lenguaje',
                    domain: 'music',
                    type: 'system',
                    capabilities: ['chord_progression', 'melody_creation', 'rhythm_patterns', 'style_analysis'],
                    created_at: datetime(),
                    group_id: 'musical_generation'
                })
            """, uuid=str(uuid.uuid4()))
            
            # 2. Crear nodos de Teoría Musical
            music_concepts = [
                {
                    "name": "Escalas Musicales",
                    "summary": "Secuencias ordenadas de notas que forman la base melódica",
                    "type": "theory",
                    "examples": ["Mayor", "Menor", "Pentatónica", "Blues"],
                    "pattern": "T-T-S-T-T-T-S (Mayor)"
                },
                {
                    "name": "Progresiones de Acordes", 
                    "summary": "Secuencias de acordes que crean estructura armónica",
                    "type": "harmony",
                    "examples": ["I-V-vi-IV", "ii-V-I", "12-bar Blues"],
                    "usage": "Base armónica de canciones"
                },
                {
                    "name": "Patrones Rítmicos",
                    "summary": "Estructuras de tiempo que definen el groove musical",
                    "type": "rhythm", 
                    "examples": ["4/4 Basic", "Shuffle", "Latin Clave"],
                    "notation": "K-S-K-S (Kick-Snare)"
                },
                {
                    "name": "Modos Musicales",
                    "summary": "Variaciones de escalas con diferentes caracteres emocionales",
                    "type": "modal_theory",
                    "examples": ["Ionian", "Dorian", "Phrygian", "Lydian"],
                    "characteristics": "Cada modo tiene color tonal único"
                }
            ]
            
            print("📚 Creando nodos de teoría musical...")
            for concept in music_concepts:
                session.run("""
                    CREATE (c:Entity:MusicConcept {
                        uuid: $uuid,
                        name: $name,
                        summary: $summary,
                        domain: 'music',
                        type: $type,
                        examples: $examples,
                        created_at: datetime(),
                        group_id: 'musical_generation'
                    })
                """, 
                uuid=str(uuid.uuid4()),
                name=concept["name"],
                summary=concept["summary"],
                type=concept["type"],
                examples=concept["examples"]
                )
            
            # 3. Crear nodos de Géneros Musicales
            genres = [
                {
                    "name": "Pop",
                    "characteristics": ["Melodías pegadizas", "Estructuras simples", "Progresión I-V-vi-IV"],
                    "tempo_range": "90-130 BPM",
                    "instruments": ["Piano", "Guitarra", "Batería", "Bajo"]
                },
                {
                    "name": "Jazz", 
                    "characteristics": ["Armonía compleja", "Improvisación", "Swing feel"],
                    "tempo_range": "60-200 BPM",
                    "instruments": ["Piano", "Saxofón", "Trompeta", "Contrabajo"]
                },
                {
                    "name": "Blues",
                    "characteristics": ["12-bar form", "Blue notes", "Call-response"],
                    "tempo_range": "60-120 BPM", 
                    "instruments": ["Guitarra", "Armónica", "Piano", "Batería"]
                },
                {
                    "name": "Electronic",
                    "characteristics": ["Sonidos sintéticos", "Ritmos programados", "Build-ups"],
                    "tempo_range": "120-150 BPM",
                    "instruments": ["Sintetizador", "Drum Machine", "Sampler"]
                }
            ]
            
            print("🎭 Creando nodos de géneros musicales...")
            for genre in genres:
                session.run("""
                    CREATE (g:Entity:MusicGenre {
                        uuid: $uuid,
                        name: $name,
                        summary: $summary,
                        domain: 'music',
                        type: 'genre',
                        characteristics: $characteristics,
                        tempo_range: $tempo_range,
                        typical_instruments: $instruments,
                        created_at: datetime(),
                        group_id: 'musical_generation'
                    })
                """,
                uuid=str(uuid.uuid4()),
                name=genre["name"],
                summary=f"Género musical {genre['name']} con características específicas",
                characteristics=genre["characteristics"],
                tempo_range=genre["tempo_range"],
                instruments=genre["instruments"]
                )
            
            # 4. Crear nodo de Ollama AI
            print("🤖 Creando nodo de Ollama AI...")
            session.run("""
                CREATE (ai:Entity:AISystem {
                    uuid: $uuid,
                    name: 'Ollama AI Music Generator',
                    summary: 'Sistema de IA usando llama3.2:3b para análisis y generación musical',
                    domain: 'ai',
                    type: 'language_model',
                    model: 'llama3.2:3b',
                    host: '192.168.100.20:11434',
                    capabilities: ['text_analysis', 'music_theory', 'composition_advice'],
                    created_at: datetime(),
                    group_id: 'musical_generation'
                })
            """, uuid=str(uuid.uuid4()))
            
            # 5. Crear relaciones entre conceptos
            print("🔗 Creando relaciones musicales...")
            
            relationships = [
                # Generación Musical conecta con teoría
                ("Generación Musical", "USES", "Escalas Musicales"),
                ("Generación Musical", "USES", "Progresiones de Acordes"),
                ("Generación Musical", "USES", "Patrones Rítmicos"),
                ("Generación Musical", "USES", "Modos Musicales"),
                
                # Teoría musical se relaciona entre sí
                ("Escalas Musicales", "FORMS_BASIS_FOR", "Modos Musicales"),
                ("Escalas Musicales", "CREATES", "Progresiones de Acordes"),
                ("Progresiones de Acordes", "COMBINES_WITH", "Patrones Rítmicos"),
                
                # Géneros usan teoría
                ("Pop", "USES", "Progresiones de Acordes"),
                ("Jazz", "USES", "Modos Musicales"), 
                ("Blues", "USES", "Escalas Musicales"),
                ("Electronic", "USES", "Patrones Rítmicos"),
                
                # AI potencia el sistema
                ("Ollama AI Music Generator", "POWERS", "Generación Musical"),
                ("Generación Musical", "GENERATES", "Pop"),
                ("Generación Musical", "GENERATES", "Jazz"),
                ("Generación Musical", "GENERATES", "Blues"),
                ("Generación Musical", "GENERATES", "Electronic")
            ]
            
            for source, rel_type, target in relationships:
                session.run("""
                    MATCH (s {name: $source}), (t {name: $target})
                    CREATE (s)-[r:RELATIONSHIP {
                        type: $rel_type,
                        created_at: datetime(),
                        context: 'musical_generation_system'
                    }]->(t)
                """, source=source, target=target, rel_type=rel_type)
            
            # 6. Crear episodios de ejemplo con Ollama
            print("📝 Creando episodios de generación...")
            
            episodes = [
                {
                    "name": "Progresión Pop C-G-Am-F",
                    "content": "Progresión de acordes generada por Ollama: C-G-Am-F (I-V-vi-IV). Ideal para canciones pop alegres y pegadizas.",
                    "ai_model": "llama3.2:3b",
                    "query": "chord progression for happy pop song",
                    "result": "C-G-Am-F"
                },
                {
                    "name": "Análisis Jazz Bebop",
                    "content": "Ollama sugiere: Dm7-G7-Cmaj7 a 170 BPM para jazz bebop uptempo con piano y saxofón.",
                    "ai_model": "llama3.2:3b", 
                    "query": "jazz bebop uptempo composition",
                    "result": "Dm7-G7-Cmaj7, 170 BPM, swing feel"
                },
                {
                    "name": "Blues en Mi Eléctrico",
                    "content": "Ollama recomienda: Progresión blues en E con guitarra eléctrica, tempo 80 BPM, usar escala pentatónica menor.",
                    "ai_model": "llama3.2:3b",
                    "query": "electric guitar blues in E",
                    "result": "E blues progression, 80 BPM, pentatonic minor"
                }
            ]
            
            for episode in episodes:
                session.run("""
                    CREATE (e:EpisodicNode:MusicGeneration {
                        uuid: $uuid,
                        name: $name,
                        episode_body: $content,
                        domain: 'music',
                        source_description: $source_desc,
                        ai_model: $ai_model,
                        user_query: $user_query,
                        ai_result: $ai_result,
                        created_at: datetime(),
                        group_id: 'musical_generation'
                    })
                """,
                uuid=str(uuid.uuid4()),
                name=episode["name"],
                content=episode["content"],
                source_desc=f"Generado por {episode['ai_model']}",
                ai_model=episode["ai_model"],
                user_query=episode["query"],
                ai_result=episode["result"]
                )
            
            # 7. Conectar episodios con conceptos
            print("🎵 Conectando episodios con conceptos musicales...")
            
            episode_connections = [
                ("Progresión Pop C-G-Am-F", "DEMONSTRATES", "Progresiones de Acordes"),
                ("Progresión Pop C-G-Am-F", "EXAMPLE_OF", "Pop"),
                ("Análisis Jazz Bebop", "DEMONSTRATES", "Jazz"),
                ("Análisis Jazz Bebop", "USES", "Modos Musicales"),
                ("Blues en Mi Eléctrico", "DEMONSTRATES", "Blues"),
                ("Blues en Mi Eléctrico", "USES", "Escalas Musicales")
            ]
            
            for episode, rel_type, concept in episode_connections:
                session.run("""
                    MATCH (e:EpisodicNode {name: $episode}), (c {name: $concept})
                    CREATE (e)-[r:RELATIONSHIP {
                        type: $rel_type,
                        created_at: datetime(),
                        context: 'ai_generated_example'
                    }]->(c)
                """, episode=episode, concept=concept, rel_type=rel_type)
            
            # 8. Conectar episodios con Ollama
            session.run("""
                MATCH (e:EpisodicNode), (ai:AISystem {name: 'Ollama AI Music Generator'})
                WHERE e.domain = 'music'
                CREATE (e)-[r:GENERATED_BY {
                    created_at: datetime(),
                    model: e.ai_model
                }]->(ai)
            """)
            
            # Verificar creación
            print("\n📊 Verificando grafo musical creado...")
            
            result = session.run("""
                MATCH (n) 
                WHERE n.domain = 'music' OR n.group_id = 'musical_generation'
                RETURN count(n) as total_nodes, 
                       count(DISTINCT labels(n)) as node_types
            """)
            stats = result.single()
            
            result = session.run("""
                MATCH (n)-[r]->(m) 
                WHERE (n.domain = 'music' OR n.group_id = 'musical_generation')
                   OR (m.domain = 'music' OR m.group_id = 'musical_generation')
                RETURN count(r) as total_relationships
            """)
            rel_stats = result.single()
            
            print(f"   ✅ {stats['total_nodes']} nodos musicales creados")
            print(f"   ✅ {rel_stats['total_relationships']} relaciones creadas")
            
            # Mostrar estructura del grafo
            print("\n🌐 Estructura del grafo musical:")
            result = session.run("""
                MATCH (n) 
                WHERE n.domain = 'music' OR n.group_id = 'musical_generation'
                RETURN labels(n) as node_type, n.name as name, n.type as concept_type
                ORDER BY node_type, name
            """)
            
            current_type = None
            for record in result:
                node_labels = record["node_type"]
                main_label = [l for l in node_labels if l not in ['Entity', 'EpisodicNode']][0] if len(node_labels) > 1 else node_labels[0]
                
                if main_label != current_type:
                    current_type = main_label
                    print(f"\n   {main_label}:")
                
                print(f"      • {record['name']}")
                
    finally:
        driver.close()

def print_neo4j_queries():
    """Mostrar queries útiles para explorar el grafo musical"""
    print("\n🔍 QUERIES PARA EXPLORAR EL GRAFO MUSICAL")
    print("=" * 50)
    
    queries = [
        ("Ver todo el grafo musical", """
            MATCH (n)-[r]-(m) 
            WHERE n.domain = 'music' OR n.group_id = 'musical_generation'
               OR m.domain = 'music' OR m.group_id = 'musical_generation'
            RETURN n, r, m
        """),
        ("Ver nodo principal de Generación Musical", """
            MATCH (gm:MusicConcept {name: 'Generación Musical'})-[r]-(connected)
            RETURN gm, r, connected
        """),
        ("Ver episodios generados por Ollama", """
            MATCH (e:EpisodicNode)-[r:GENERATED_BY]->(ai:AISystem)
            WHERE e.domain = 'music'
            RETURN e, r, ai
        """),
        ("Ver géneros musicales y sus características", """
            MATCH (g:MusicGenre)
            RETURN g.name as genre, g.characteristics as characteristics, g.tempo_range as tempo
        """),
        ("Ver teoría musical y sus relaciones", """
            MATCH (theory:MusicConcept)-[r]-(connected)
            WHERE theory.type IN ['theory', 'harmony', 'rhythm', 'modal_theory']
            RETURN theory, r, connected
        """)
    ]
    
    for i, (desc, query) in enumerate(queries, 1):
        print(f"\n{i}. {desc}:")
        print(f"```cypher")
        print(query.strip())
        print("```")

if __name__ == "__main__":
    print("🎵 CREANDO GRAFO DE CONOCIMIENTO MUSICAL EN NEO4J")
    print(f"Fecha: {datetime.now()}")
    print("=" * 60)
    
    try:
        create_musical_knowledge_graph()
        print_neo4j_queries()
        
        print(f"\n✅ GRAFO MUSICAL CREADO EXITOSAMENTE")
        print(f"🌐 Abrir Neo4j Browser: http://localhost:7474")
        print(f"👤 Usuario: neo4j | 🔒 Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Verificar que Neo4j esté ejecutándose en localhost:7687")