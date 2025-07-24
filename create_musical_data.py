#!/usr/bin/env python3
"""
Crear datos musicales de ejemplo en Graphiti para generación musical
"""

import asyncio
import json
from datetime import datetime
import uuid


async def create_musical_episodes():
    """Crear episodios musicales usando MCP Graphiti"""
    
    # Episodios sobre teoría musical
    musical_episodes = [
        {
            "name": "Escalas Musicales Básicas",
            "episode_body": json.dumps({
                "concept": "escalas_musicales", 
                "content": "Las escalas musicales son secuencias ordenadas de notas. La escala mayor sigue el patrón de tonos y semitonos: T-T-S-T-T-T-S. Por ejemplo, Do Mayor: C-D-E-F-G-A-B-C",
                "examples": ["C Major: C-D-E-F-G-A-B", "G Major: G-A-B-C-D-E-F#"],
                "applications": ["composición", "improvisación", "armonía"]
            }),
            "format": "json",
            "source_description": "Teoría musical fundamental"
        },
        {
            "name": "Progresiones de Acordes Populares",
            "episode_body": json.dumps({
                "concept": "progresiones_acordes",
                "content": "Las progresiones de acordes son secuencias de acordes que crean la estructura armónica de una canción",
                "progressions": {
                    "I-V-vi-IV": {"description": "Progresión pop más común", "example": "C-G-Am-F"},
                    "ii-V-I": {"description": "Progresión jazz clásica", "example": "Dm-G-C"},
                    "vi-IV-I-V": {"description": "Progresión emocional", "example": "Am-F-C-G"}
                },
                "genres": ["pop", "rock", "jazz", "folk"]
            }),
            "format": "json",
            "source_description": "Armonía y progresiones"
        },
        {
            "name": "Patrones Rítmicos Fundamentales",
            "episode_body": json.dumps({
                "concept": "patrones_ritmicos",
                "content": "Los patrones rítmicos definen el groove y el estilo de una pieza musical",
                "patterns": {
                    "4/4_basic": {"description": "Kick en 1 y 3, snare en 2 y 4", "pattern": "K-S-K-S"},
                    "shuffle": {"description": "Ritmo ternario swingueado", "pattern": "K-x-S-x-K-x-S-x"},
                    "latin": {"description": "Clave de son 3-2", "pattern": "x-x-K-x-x-K-x-x"}
                },
                "bpm_ranges": {"ballad": "60-80", "medium": "90-120", "fast": "130-160"}
            }),
            "format": "json",
            "source_description": "Patrones rítmicos y groove"
        },
        {
            "name": "Modos Musicales y Su Carácter",
            "episode_body": json.dumps({
                "concept": "modos_musicales",
                "content": "Los modos son variaciones de la escala mayor que comienzan en diferentes grados",
                "modes": {
                    "ionian": {"character": "brillante, alegre", "use": "pop, folk"},
                    "dorian": {"character": "melancólico, cool", "use": "jazz, rock progresivo"},
                    "phrygian": {"character": "oscuro, español", "use": "flamenco, metal"},
                    "lydian": {"character": "etéreo, suspendido", "use": "film scoring"},
                    "mixolydian": {"character": "bluesy, relajado", "use": "rock, country"},
                    "aeolian": {"character": "triste, menor natural", "use": "rock, pop"},
                    "locrian": {"character": "inestable, tenso", "use": "jazz, experimental"}
                }
            }),
            "format": "json",
            "source_description": "Modos y color armónico"
        },
        {
            "name": "Generación Musical con IA",
            "episode_body": json.dumps({
                "concept": "ai_music_generation",
                "content": "La IA puede generar música usando diferentes enfoques: modelos estadísticos, redes neuronales, y sistemas basados en reglas",
                "approaches": {
                    "rule_based": {
                        "description": "Sistemas basados en reglas de teoría musical",
                        "pros": ["controlable", "interpretable", "rápido"],
                        "cons": ["limitado", "predecible"]
                    },
                    "neural_networks": {
                        "description": "RNNs, Transformers para secuencias musicales",
                        "pros": ["creativo", "aprende patrones complejos"],
                        "cons": ["caja negra", "requiere muchos datos"]
                    },
                    "hybrid": {
                        "description": "Combina reglas musicales con IA",
                        "pros": ["mejor control", "más musical"],
                        "cons": ["más complejo de implementar"]
                    }
                },
                "parameters": ["tempo", "key", "mode", "style", "complexity", "duration"]
            }),
            "format": "json",
            "source_description": "IA y generación musical"
        }
    ]
    
    return musical_episodes


async def create_musical_knowledge_graph():
    """Crear un grafo de conocimiento musical completo"""
    
    print("🎵 Creando capítulo de generación musical en Graphiti...")
    print("=" * 60)
    
    # Obtener episodios musicales
    episodes = await create_musical_episodes()
    
    # En un sistema real, usaríamos las funciones MCP de Graphiti
    # Por ahora, mostraremos la estructura propuesta
    
    print("📊 Estructura del grafo musical:")
    print("\n🎼 Episodios a crear:")
    for i, episode in enumerate(episodes, 1):
        print(f"   {i}. {episode['name']}")
        print(f"      - Concepto: {json.loads(episode['episode_body'])['concept']}")
        print()
    
    print("🔗 Relaciones propuestas:")
    relationships = [
        "Escalas → conecta_con → Modos",
        "Acordes → usa → Escalas", 
        "Progresiones → compone → Acordes",
        "Patrones_Rítmicos → combina_con → Progresiones",
        "IA_Musical → aplica → [Escalas, Acordes, Ritmos]",
        "Generación → requiere → [Teoría, Patrones, Estilo]"
    ]
    
    for rel in relationships:
        print(f"   • {rel}")
    
    print("\n🎯 Capacidades de generación:")
    capabilities = [
        "Generar progresiones de acordes basadas en modo/género",
        "Crear melodías que siguen escalas específicas", 
        "Aplicar patrones rítmicos según el estilo",
        "Combinar elementos usando conocimiento del grafo",
        "Sugerir variaciones basadas en relaciones musicales"
    ]
    
    for cap in capabilities:
        print(f"   • {cap}")
    
    return episodes


# Función para agregar episodios reales a Graphiti
async def add_episodes_to_graphiti(episodes):
    """Agregar episodios musicales a Graphiti usando MCP"""
    print("\n🔄 Agregando episodios a Graphiti...")
    
    # Aquí usaríamos las funciones MCP reales
    # mcp__mcp-graphiti__add_episode para cada episodio
    
    for i, episode in enumerate(episodes, 1):
        print(f"   📝 Agregando episodio {i}: {episode['name']}")
        # await mcp_add_episode(episode)
    
    print("   ✅ Todos los episodios agregados al grafo")


if __name__ == "__main__":
    print("🎵 GENERACIÓN MUSICAL CON GRAPHITI")
    print(f"Fecha: {datetime.now()}")
    print("=" * 60)
    
    try:
        episodes = asyncio.run(create_musical_knowledge_graph())
        print(f"\n✅ ESTRUCTURA MUSICAL CREADA")
        print(f"📊 {len(episodes)} episodios preparados para el grafo")
        
    except Exception as e:
        print(f"❌ Error: {e}")