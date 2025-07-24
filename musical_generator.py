#!/usr/bin/env python3
"""
Generador Musical basado en Graphiti Knowledge Graph
Usa el conocimiento musical almacenado en el grafo para generar música
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Any


class MusicalGenerator:
    """Generador musical que usa conocimiento del grafo Graphiti"""
    
    def __init__(self):
        self.knowledge_base = {
            "scales": {
                "major": {"pattern": "T-T-S-T-T-T-S", "mood": "happy", "notes": ["C", "D", "E", "F", "G", "A", "B"]},
                "minor": {"pattern": "T-S-T-T-S-T-T", "mood": "sad", "notes": ["A", "B", "C", "D", "E", "F", "G"]},
                "pentatonic": {"pattern": "T-T-TS-T-TS", "mood": "simple", "notes": ["C", "D", "E", "G", "A"]}
            },
            "progressions": {
                "pop": {"chords": ["I", "V", "vi", "IV"], "example": "C-G-Am-F", "mood": "catchy"},
                "jazz": {"chords": ["ii", "V", "I"], "example": "Dm-G-C", "mood": "sophisticated"},
                "blues": {"chords": ["I", "IV", "V"], "example": "C-F-G", "mood": "groovy"}
            },
            "rhythms": {
                "4/4_basic": {"pattern": "K-S-K-S", "bpm": "90-120", "style": "pop"},
                "shuffle": {"pattern": "K-x-S-x-K-x-S-x", "bpm": "80-100", "style": "blues"},
                "latin": {"pattern": "x-x-K-x-x-K-x-x", "bpm": "100-140", "style": "latin"}
            },
            "modes": {
                "ionian": {"character": "bright", "usage": "pop"},
                "dorian": {"character": "cool", "usage": "jazz"},
                "phrygian": {"character": "dark", "usage": "metal"},
                "lydian": {"character": "ethereal", "usage": "film"}
            }
        }
    
    async def search_musical_knowledge(self, query: str) -> Dict[str, Any]:
        """Buscar conocimiento musical en el grafo (simulado)"""
        # En un sistema real, usaríamos: mcp__mcp-graphiti__search_nodes(query)
        results = {}
        
        if "scale" in query.lower():
            results = self.knowledge_base["scales"]
        elif "chord" in query.lower() or "progression" in query.lower():
            results = self.knowledge_base["progressions"]
        elif "rhythm" in query.lower():
            results = self.knowledge_base["rhythms"]
        elif "mode" in query.lower():
            results = self.knowledge_base["modes"]
        
        return results
    
    def generate_chord_progression(self, style: str = "pop", key: str = "C") -> Dict[str, Any]:
        """Generar progresión de acordes basada en el estilo"""
        
        if style not in self.knowledge_base["progressions"]:
            style = "pop"
        
        progression_info = self.knowledge_base["progressions"][style]
        
        # Mapear grados a acordes en la tonalidad especificada
        chord_mapping = {
            "C": {"I": "C", "ii": "Dm", "iii": "Em", "IV": "F", "V": "G", "vi": "Am", "vii°": "Bdim"},
            "G": {"I": "G", "ii": "Am", "iii": "Bm", "IV": "C", "V": "D", "vi": "Em", "vii°": "F#dim"},
            "Am": {"i": "Am", "ii°": "Bdim", "III": "C", "iv": "Dm", "v": "Em", "VI": "F", "VII": "G"}
        }
        
        base_chords = chord_mapping.get(key, chord_mapping["C"])
        roman_numerals = progression_info["chords"]
        
        actual_chords = []
        for numeral in roman_numerals:
            if numeral in base_chords:
                actual_chords.append(base_chords[numeral])
            else:
                # Fallback para casos no mapeados
                actual_chords.append(numeral)
        
        return {
            "style": style,
            "key": key,
            "roman_numerals": roman_numerals,
            "chords": actual_chords,
            "mood": progression_info["mood"],
            "description": f"Progresión {style} en {key}: {'-'.join(actual_chords)}"
        }
    
    def generate_melody(self, scale_type: str = "major", key: str = "C", length: int = 8) -> Dict[str, Any]:
        """Generar melodía basada en la escala"""
        
        if scale_type not in self.knowledge_base["scales"]:
            scale_type = "major"
        
        scale_info = self.knowledge_base["scales"][scale_type]
        base_notes = scale_info["notes"]
        
        # Generar secuencia melódica aleatoria
        melody_notes = []
        for _ in range(length):
            note = random.choice(base_notes)
            octave = random.choice([3, 4, 5])  # Octavas medias
            melody_notes.append(f"{note}{octave}")
        
        return {
            "scale": scale_type,
            "key": key,
            "notes": melody_notes,
            "mood": scale_info["mood"],
            "pattern": scale_info["pattern"],
            "description": f"Melodía {scale_type} en {key} con {length} notas"
        }
    
    def generate_rhythm_pattern(self, style: str = "4/4_basic", bars: int = 4) -> Dict[str, Any]:
        """Generar patrón rítmico"""
        
        if style not in self.knowledge_base["rhythms"]:
            style = "4/4_basic"
        
        rhythm_info = self.knowledge_base["rhythms"][style]
        base_pattern = rhythm_info["pattern"].split("-")
        
        # Repetir el patrón para el número de compases
        full_pattern = []
        for _ in range(bars):
            full_pattern.extend(base_pattern)
        
        return {
            "style": style,
            "pattern": full_pattern,
            "bars": bars,
            "bpm_range": rhythm_info["bpm"],
            "musical_style": rhythm_info["style"],
            "description": f"Patrón rítmico {style} por {bars} compases"
        }
    
    def generate_complete_song(self, style: str = "pop", key: str = "C", tempo: int = 120) -> Dict[str, Any]:
        """Generar una canción completa combinando todos los elementos"""
        
        # Buscar conocimiento relacionado
        progression = self.generate_chord_progression(style, key)
        melody = self.generate_melody("major" if "major" in key else "minor", key, 16)
        rhythm = self.generate_rhythm_pattern("4/4_basic", 8)
        
        # Seleccionar modo apropiado
        mode_style = "ionian" if style == "pop" else "dorian" if style == "jazz" else "mixolydian"
        mode_info = self.knowledge_base["modes"].get(mode_style, self.knowledge_base["modes"]["ionian"])
        
        song_structure = {
            "metadata": {
                "title": f"Canción generada en {key} {style}",
                "style": style,
                "key": key,
                "tempo": tempo,
                "mode": mode_style,
                "mood": progression["mood"],
                "generated_at": datetime.now().isoformat()
            },
            "harmonic_structure": progression,
            "melodic_line": melody,
            "rhythmic_pattern": rhythm,
            "modal_characteristics": {
                "mode": mode_style,
                "character": mode_info["character"],
                "typical_usage": mode_info["usage"]
            },
            "generation_parameters": {
                "approach": "hybrid",  # Reglas musicales + IA
                "knowledge_source": "graphiti_musical_graph",
                "creativity_level": "medium"
            }
        }
        
        return song_structure
    
    async def interactive_generation(self):
        """Generación interactiva basada en consultas"""
        print("🎵 GENERADOR MUSICAL INTERACTIVO")
        print("=" * 50)
        print("Basado en conocimiento del grafo Graphiti")
        print()
        
        # Ejemplo de consultas
        queries = [
            "¿Qué progresión de acordes uso para una canción pop?",
            "¿Cómo creo una melodía en modo dorian?",
            "¿Qué patrón rítmico funciona para blues?",
            "Genera una canción completa en estilo jazz"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"🔍 Consulta {i}: {query}")
            
            if "progresión" in query and "pop" in query:
                result = self.generate_chord_progression("pop", "C")
                print(f"   📊 Resultado: {result['description']}")
                print(f"   🎹 Acordes: {' - '.join(result['chords'])}")
            
            elif "melodía" in query and "dorian" in query:
                result = self.generate_melody("minor", "D", 12)  # Dorian aproximado
                print(f"   📊 Resultado: {result['description']}")
                print(f"   🎵 Notas: {' - '.join(result['notes'][:6])}...")
            
            elif "rítmico" in query and "blues" in query:
                result = self.generate_rhythm_pattern("shuffle", 4)
                print(f"   📊 Resultado: {result['description']}")
                print(f"   🥁 Patrón: {'-'.join(result['pattern'][:8])}")
            
            elif "canción completa" in query and "jazz" in query:
                result = self.generate_complete_song("jazz", "Dm", 110)
                print(f"   📊 Resultado: {result['metadata']['title']}")
                print(f"   🎼 Acordes: {' - '.join(result['harmonic_structure']['chords'])}")
                print(f"   🎵 Tempo: {result['metadata']['tempo']} BPM")
                print(f"   🎭 Carácter: {result['modal_characteristics']['character']}")
            
            print()
        
        return True


async def main():
    """Función principal para demostrar el generador musical"""
    
    print("🎯 DEMOSTRACIÓN DEL GENERADOR MUSICAL GRAPHITI")
    print(f"Fecha: {datetime.now()}")
    print("=" * 60)
    
    generator = MusicalGenerator()
    
    # Demostración interactiva
    await generator.interactive_generation()
    
    print("🎼 EJEMPLOS DE GENERACIÓN ESPECÍFICA")
    print("=" * 40)
    
    # Generar ejemplos específicos
    examples = [
        ("Balada Pop", "pop", "G", 75),
        ("Jazz Standard", "jazz", "Bb", 120),
        ("Blues Shuffle", "blues", "E", 95)
    ]
    
    for name, style, key, tempo in examples:
        print(f"\n🎵 Generando: {name}")
        song = generator.generate_complete_song(style, key, tempo)
        
        print(f"   🔑 Tonalidad: {song['metadata']['key']}")
        print(f"   🎼 Acordes: {' → '.join(song['harmonic_structure']['chords'])}")
        print(f"   ⏱️  Tempo: {song['metadata']['tempo']} BPM")
        print(f"   🎭 Mood: {song['metadata']['mood']}")
        print(f"   🎯 Modo: {song['modal_characteristics']['mode']} ({song['modal_characteristics']['character']})")
    
    print(f"\n✅ GENERACIÓN MUSICAL COMPLETADA")
    print("🔗 Usando conocimiento estructurado del grafo Graphiti")


if __name__ == "__main__":
    asyncio.run(main())