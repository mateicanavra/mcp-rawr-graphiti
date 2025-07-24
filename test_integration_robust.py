#!/usr/bin/env python3
"""
Script de prueba ROBUSTO para la integración entre Graphiti MCP Server y Ollama
Incluye manejo de errores, reintentos y verificación de que los datos se guarden en Neo4j
"""

import requests
import json
import time
from datetime import datetime
from neo4j import GraphDatabase

# Configuración
OLLAMA_URL = "http://192.168.100.20:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
GRAPHITI_MCP_URL = "http://localhost:8000/messages/"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

def ask_ollama(prompt: str) -> str:
    """Hacer pregunta a Ollama en la VM"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )
        response.raise_for_status()
        return response.json().get("response", "Sin respuesta")
    except requests.RequestException as e:
        return f"Error al llamar a Ollama: {str(e)}"

def get_fresh_session_id():
    """Obtener un session ID fresco desde el servidor MCP"""
    try:
        response = requests.get(f"http://localhost:8000/sse", timeout=10)
        for line in response.text.split('\n'):
            if 'session_id=' in line:
                session_id = line.split('session_id=')[1].strip()
                print(f"   Nuevo Session ID: {session_id}")
                return session_id
        return None
    except Exception as e:
        print(f"   Error obteniendo session ID: {e}")
        return None

def add_episode_to_graphiti_robust(name: str, content: str, group_id: str = "test_integration", max_retries: int = 3):
    """Agregar episodio a Graphiti con reintentos y manejo robusto de errores"""
    
    for attempt in range(max_retries):
        print(f"   Intento {attempt + 1}/{max_retries}...")
        
        # Obtener session ID fresco para cada intento
        session_id = get_fresh_session_id()
        if not session_id:
            print(f"   ❌ No se pudo obtener session ID")
            continue
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tool",
            "params": {
                "name": "add_episode",
                "input": {
                    "name": name,
                    "episode_body": content,
                    "format": "text",
                    "source_description": "Integración Ollama-Graphiti ROBUST",
                    "group_id": group_id
                }
            },
            "id": int(time.time()) + attempt
        }
        
        try:
            response = requests.post(
                f"{GRAPHITI_MCP_URL}?session_id={session_id}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            result = response.text
            print(f"   Respuesta: {result}")
            
            # Verificar si fue exitoso
            if "Accepted" in result or response.status_code == 200:
                print(f"   ✅ Episodio enviado exitosamente (intento {attempt + 1})")
                return result
            else:
                print(f"   ⚠️ Respuesta inesperada: {result}")
                
        except requests.RequestException as e:
            print(f"   ❌ Error en intento {attempt + 1}: {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"   Esperando 5 segundos antes del siguiente intento...")
            time.sleep(5)
    
    return f"❌ Falló después de {max_retries} intentos"

def check_neo4j_data():
    """Verificar si hay datos en Neo4j"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Contar nodos totales
            result = session.run("MATCH (n) RETURN count(n) as total")
            total = result.single()["total"]
            
            # Contar episodios específicos de prueba
            result = session.run("""
                MATCH (e:EpisodicNode) 
                WHERE e.source_description CONTAINS 'Ollama-Graphiti'
                RETURN count(e) as test_episodes
            """)
            test_episodes = result.single()["test_episodes"]
            
            print(f"   📊 Total nodos en Neo4j: {total}")
            print(f"   📄 Episodios de prueba: {test_episodes}")
            
            return total, test_episodes
            
    except Exception as e:
        print(f"   ❌ Error verificando Neo4j: {e}")
        return 0, 0

def wait_and_verify_processing(episode_name: str, max_wait: int = 60):
    """Esperar y verificar que el episodio se procese en Neo4j"""
    print(f"   ⏳ Esperando procesamiento de '{episode_name}'...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("""
                    MATCH (e:EpisodicNode) 
                    WHERE e.name CONTAINS $name_part
                    RETURN count(e) as found
                """, name_part=episode_name.split(' - ')[0])
                
                found = result.single()["found"]
                if found > 0:
                    print(f"   ✅ Episodio encontrado en Neo4j después de {int(time.time() - start_time)} segundos")
                    return True
                    
        except Exception as e:
            print(f"   ⚠️ Error verificando: {e}")
        
        print(f"   ⏳ Esperando... ({int(time.time() - start_time)}s)")
        time.sleep(5)
    
    print(f"   ❌ Episodio no apareció en Neo4j después de {max_wait} segundos")
    return False

def create_direct_episode_in_neo4j(name: str, content: str):
    """Crear episodio directamente en Neo4j como fallback"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            session.run("""
                CREATE (e:EpisodicNode {
                    uuid: randomUUID(),
                    name: $name,
                    episode_body: $content,
                    created_at: datetime(),
                    source_description: 'Creado directamente en Neo4j (fallback)',
                    group_id: 'test_integration_direct'
                })
            """, name=name, content=content)
            
        print(f"   ✅ Episodio creado directamente en Neo4j")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creando episodio directo: {e}")
        return False

def main():
    print("🚀 PRUEBA DE INTEGRACIÓN OLLAMA + GRAPHITI (VERSIÓN ROBUSTA)")
    print(f"Fecha: {datetime.now()}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Modelo: {OLLAMA_MODEL}")
    print(f"Graphiti MCP URL: {GRAPHITI_MCP_URL}")
    print("=" * 70)
    
    # 0. Verificar estado inicial de Neo4j
    print("\\n0. Verificando estado inicial de Neo4j...")
    initial_total, initial_episodes = check_neo4j_data()
    
    # 1. Probar conexión con Ollama
    print("\\n1. Probando conexión con Ollama...")
    test_prompt = "¿Qué ventajas tiene usar Graphiti para memoria de IA?"
    ollama_response = ask_ollama(test_prompt)
    print(f"Pregunta: {test_prompt}")
    if "Error" in ollama_response:
        print(f"❌ {ollama_response}")
        return
    else:
        print(f"✅ Respuesta recibida: {ollama_response[:150]}...")
    
    # 2. Intentar guardar en Graphiti con reintentos
    print("\\n2. Guardando respuesta en Graphiti (con reintentos)...")
    episode_name = f"Ollama Robust Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    episode_content = f"Pregunta: {test_prompt}\\n\\nRespuesta de Ollama ({OLLAMA_MODEL}): {ollama_response}"
    
    graphiti_result = add_episode_to_graphiti_robust(episode_name, episode_content)
    
    # 3. Verificar si se guardó en Neo4j
    print("\\n3. Verificando si se guardó en Neo4j...")
    if "Accepted" in str(graphiti_result):
        success = wait_and_verify_processing(episode_name, max_wait=45)
        
        if not success:
            print("\\n⚠️ El episodio no apareció en Neo4j. Creando directamente como fallback...")
            create_direct_episode_in_neo4j(episode_name, episode_content)
    else:
        print("\\n❌ Graphiti MCP falló. Creando episodio directamente en Neo4j...")
        create_direct_episode_in_neo4j(episode_name, episode_content)
    
    # 4. Verificar estado final
    print("\\n4. Verificando estado final de Neo4j...")
    final_total, final_episodes = check_neo4j_data()
    
    print(f"\\n📊 RESUMEN:")
    print(f"   • Nodos iniciales: {initial_total} → Finales: {final_total}")
    print(f"   • Episodios iniciales: {initial_episodes} → Finales: {final_episodes}")
    print(f"   • Nuevos episodios: {final_episodes - initial_episodes}")
    
    if final_episodes > initial_episodes:
        print("\\n✅ ¡ÉXITO! Se agregaron nuevos episodios a Neo4j")
        print("\\n🌐 Para ver los datos:")
        print("   1. Abrir: http://localhost:7474")
        print("   2. Conectar con usuario 'neo4j', password 'admin123'")
        print("   3. Query: MATCH (e:EpisodicNode) RETURN e ORDER BY e.created_at DESC")
    else:
        print("\\n❌ No se agregaron episodios nuevos")
    
    print("\\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    main()