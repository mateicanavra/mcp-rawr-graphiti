#!/usr/bin/env python3
"""
Script para verificar qué datos hay en Neo4j y mostrar queries útiles
"""

from neo4j import GraphDatabase
import os
from datetime import datetime

# Configuración
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

def check_neo4j_connection():
    """Verificar conexión a Neo4j"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ Conexión a Neo4j exitosa")
        return driver
    except Exception as e:
        print(f"❌ Error conectando a Neo4j: {e}")
        return None

def get_database_stats(driver):
    """Obtener estadísticas de la base de datos"""
    print("\n🔍 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 50)
    
    with driver.session() as session:
        # Contar todos los nodos
        result = session.run("MATCH (n) RETURN count(n) as total_nodes")
        total_nodes = result.single()["total_nodes"]
        print(f"📊 Total de nodos: {total_nodes}")
        
        # Contar todas las relaciones
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
        total_rels = result.single()["total_relationships"]
        print(f"🔗 Total de relaciones: {total_rels}")
        
        # Tipos de nodos
        result = session.run("MATCH (n) RETURN DISTINCT labels(n) as labels, count(n) as count")
        print(f"\n📋 TIPOS DE NODOS:")
        for record in result:
            labels = record["labels"]
            count = record["count"]
            label_str = ":".join(labels) if labels else "Sin etiqueta"
            print(f"   • {label_str}: {count}")
        
        # Tipos de relaciones
        result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
        print(f"\n🔗 TIPOS DE RELACIONES:")
        for record in result:
            rel_type = record["type"]
            count = record["count"]
            print(f"   • {rel_type}: {count}")
        
        return total_nodes, total_rels

def show_sample_data(driver):
    """Mostrar datos de ejemplo"""
    print("\n🎯 DATOS DE EJEMPLO")
    print("=" * 50)
    
    with driver.session() as session:
        # Mostrar algunos nodos
        result = session.run("MATCH (n) RETURN n LIMIT 5")
        print("📌 Primeros 5 nodos:")
        for i, record in enumerate(result, 1):
            node = record["n"]
            labels = ":".join(node.labels) if node.labels else "Sin etiqueta"
            print(f"   {i}. [{labels}] {node.get('name', node.get('uuid', 'Sin nombre'))}")
        
        # Mostrar algunas relaciones
        result = session.run("MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 3")
        print(f"\n🔗 Primeras 3 relaciones:")
        for i, record in enumerate(result, 1):
            a = record["a"]
            r = record["r"]
            b = record["b"]
            a_name = a.get('name', a.get('uuid', 'Nodo A'))[:20]
            b_name = b.get('name', b.get('uuid', 'Nodo B'))[:20]
            print(f"   {i}. {a_name} --[{r.type}]--> {b_name}")

def generate_useful_queries():
    """Generar queries útiles para usar en Neo4j Browser"""
    print("\n🚀 QUERIES ÚTILES PARA NEO4J BROWSER")
    print("=" * 50)
    
    queries = [
        {
            "title": "Ver TODOS los nodos y relaciones (grafo completo)",
            "query": "MATCH (n)-[r]-(m) RETURN n, r, m",
            "description": "Muestra todo el grafo. ⚠️ Usar solo si hay pocos datos"
        },
        {
            "title": "Ver primeros 25 nodos",
            "query": "MATCH (n) RETURN n LIMIT 25",
            "description": "Muestra los primeros 25 nodos del grafo"
        },
        {
            "title": "Ver episodios (si los hay)",
            "query": "MATCH (e:EpisodicNode) RETURN e.name, e.episode_body, e.created_at ORDER BY e.created_at DESC LIMIT 10",
            "description": "Muestra los últimos 10 episodios creados"
        },
        {
            "title": "Buscar por contenido específico",
            "query": "MATCH (n) WHERE toLower(toString(n.name)) CONTAINS 'tesla' OR toLower(toString(n.summary)) CONTAINS 'tesla' RETURN n",
            "description": "Busca nodos que contengan 'tesla' (cambiar por tu término)"
        },
        {
            "title": "Ver estructura del esquema",
            "query": "CALL db.schema.visualization()",
            "description": "Muestra la estructura del esquema de la base de datos"
        },
        {
            "title": "Nodos más conectados",
            "query": "MATCH (n)-[r]-() RETURN n.name, labels(n), count(r) as connections ORDER BY connections DESC LIMIT 10",
            "description": "Muestra los nodos con más conexiones"
        },
        {
            "title": "Ver relaciones entre entidades específicas",
            "query": "MATCH (a)-[r]->(b) WHERE a.name IS NOT NULL AND b.name IS NOT NULL RETURN a.name, type(r), b.name LIMIT 20",
            "description": "Muestra relaciones entre entidades con nombres"
        }
    ]
    
    for i, q in enumerate(queries, 1):
        print(f"\n{i}. {q['title']}")
        print(f"   📝 Query: {q['query']}")
        print(f"   💡 Descripción: {q['description']}")

def main():
    print("🔍 VERIFICADOR DE DATOS EN NEO4J")
    print(f"Fecha: {datetime.now()}")
    print(f"Conectando a: {NEO4J_URI}")
    print("=" * 60)
    
    # Verificar conexión
    driver = check_neo4j_connection()
    if not driver:
        return
    
    try:
        # Obtener estadísticas
        total_nodes, total_rels = get_database_stats(driver)
        
        if total_nodes == 0:
            print(f"\n⚠️  LA BASE DE DATOS ESTÁ VACÍA")
            print(f"   No hay nodos ni relaciones en Neo4j")
            print(f"\n💡 Para crear datos de prueba:")
            print(f"   1. Ejecutar: python3 test_integration.py")
            print(f"   2. Esperar que procese (10-15 segundos)")
            print(f"   3. Volver a verificar con este script")
        else:
            # Mostrar datos de ejemplo
            show_sample_data(driver)
        
        # Siempre mostrar queries útiles
        generate_useful_queries()
        
        print(f"\n🌐 CÓMO USAR EN NEO4J BROWSER:")
        print(f"   1. Abrir: http://localhost:7474")
        print(f"   2. Conectar con usuario: {NEO4J_USER}, password: {NEO4J_PASSWORD}")
        print(f"   3. Copiar y pegar cualquiera de los queries de arriba")
        print(f"   4. Presionar Ctrl+Enter o click en ▶️ para ejecutar")
        
    finally:
        driver.close()

if __name__ == "__main__":
    main()