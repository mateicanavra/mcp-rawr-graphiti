#!/usr/bin/env python3
"""
Sistema Completo de Generación Musical
Integra Ollama + Graphiti + Teoría Musical + AI Music Platform
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class CompleteMusicSystem:
    """Sistema completo de generación musical basado en IA y grafos de conocimiento"""
    
    def __init__(self):
        self.ollama_url = "http://192.168.100.20:11434"
        self.current_model = "llama3.2:3b"
        
        # Base de conocimiento musical expandida
        self.music_knowledge = {
            "chord_progressions": {
                "pop": {
                    "I-V-vi-IV": {"chords": ["C", "G", "Am", "F"], "mood": "uplifting", "examples": ["Let It Be", "Don't Stop Believin'"]},
                    "vi-IV-I-V": {"chords": ["Am", "F", "C", "G"], "mood": "emotional", "examples": ["Someone Like You", "Complicated"]},
                    "I-vi-IV-V": {"chords": ["C", "Am", "F", "G"], "mood": "nostalgic", "examples": ["Stand By Me", "Blue Moon"]}
                },
                "jazz": {
                    "ii-V-I": {"chords": ["Dm7", "G7", "CM7"], "mood": "sophisticated", "context": "major resolution"},
                    "vi-ii-V-I": {"chords": ["Am7", "Dm7", "G7", "CM7"], "mood": "flowing", "context": "extended resolution"},
                    "I-vi-ii-V": {"chords": ["CM7", "Am7", "Dm7", "G7"], "mood": "circular", "context": "rhythm changes"}
                },
                "blues": {
                    "12-bar": {"chords": ["C7", "C7", "C7", "C7", "F7", "F7", "C7", "C7", "G7", "F7", "C7", "G7"], "mood": "groovy"},
                    "8-bar": {"chords": ["C7", "F7", "C7", "G7"], "mood": "simple"}
                }
            },
            "scales_and_modes": {
                "major": {"notes": ["C", "D", "E", "F", "G", "A", "B"], "mood": "happy", "intervals": "W-W-H-W-W-W-H"},
                "natural_minor": {"notes": ["A", "B", "C", "D", "E", "F", "G"], "mood": "sad", "intervals": "W-H-W-W-H-W-W"},
                "dorian": {"notes": ["D", "E", "F", "G", "A", "B", "C"], "mood": "cool/medieval", "characteristic": "natural 6th"},
                "mixolydian": {"notes": ["G", "A", "B", "C", "D", "E", "F"], "mood": "bluesy", "characteristic": "flat 7th"},
                "pentatonic_major": {"notes": ["C", "D", "E", "G", "A"], "mood": "open", "use": "folk, pop, rock"},
                "pentatonic_minor": {"notes": ["A", "C", "D", "E", "G"], "mood": "bluesy", "use": "blues, rock"}
            },
            "rhythm_patterns": {
                "4/4": {
                    "basic_rock": {"pattern": "K-S-K-S", "description": "kick on 1&3, snare on 2&4"},
                    "pop_ballad": {"pattern": "K-x-S-x-K-x-S-x", "description": "simple pop feel"},
                    "funk": {"pattern": "K-x-S-K-x-S-x-K", "description": "syncopated groove"}
                },
                "3/4": {
                    "waltz": {"pattern": "K-x-x", "description": "classical waltz"},
                    "folk": {"pattern": "K-x-S", "description": "folk ballad"}
                }
            },
            "instrumentation": {
                "pop_band": ["drums", "bass", "electric_guitar", "vocals", "keyboards"],
                "acoustic": ["acoustic_guitar", "vocals", "light_percussion"],
                "jazz_combo": ["piano", "bass", "drums", "saxophone", "trumpet"],
                "electronic": ["synthesizer", "drum_machine", "bass_synth", "pad", "lead_synth"]
            }
        }
    
    async def query_ollama(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """Consultar Ollama con prompt musical"""
        try:
            payload = {
                "model": self.current_model,
                "prompt": f"""Eres un experto compositor y productor musical. Responde de forma concisa y práctica.

CONSULTA: {prompt}

Proporciona información específica sobre:
- Acordes exactos (ej: C, Dm, G7)
- Escalas/modos específicos
- BPM sugerido
- Instrumentación
- Estructura de canción si es relevante

Respuesta:""",
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return None
            
        except Exception as e:
            print(f"Error consultando Ollama: {e}")
            return None
    
    def extract_musical_elements(self, text: str) -> Dict[str, Any]:
        """Extraer elementos musicales del texto de Ollama"""
        elements = {
            "chords": [],
            "scale": None,
            "tempo": None,
            "key": None,
            "instruments": [],
            "structure": None
        }
        
        import re
        text_lower = text.lower()
        
        # Extraer acordes (formatos: C, Dm, G7, AM7, etc.)
        chord_pattern = r'\b([A-G][#b]?(?:m|maj|min|7|9|11|13|sus|dim|aug)*)\b'
        chords = re.findall(chord_pattern, text, re.IGNORECASE)
        elements["chords"] = list(set(chords))  # Remove duplicates
        
        # Extraer BPM
        bpm_match = re.search(r'(\d+)\s*bpm', text_lower)
        if bpm_match:
            elements["tempo"] = int(bpm_match.group(1))
        
        # Extraer tonalidad
        key_pattern = r'\b([A-G][#b]?)\s+(?:major|minor|maj|min)\b'
        key_match = re.search(key_pattern, text, re.IGNORECASE)
        if key_match:
            elements["key"] = key_match.group(1)
        
        # Extraer instrumentos
        instruments = ["piano", "guitar", "drums", "bass", "violin", "saxophone", "trumpet", "synthesizer"]
        for instrument in instruments:
            if instrument in text_lower:
                elements["instruments"].append(instrument)
        
        return elements
    
    def generate_from_elements(self, elements: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Generar composición musical a partir de elementos extraídos"""
        
        # Determinar estilo basado en la consulta
        style = "pop"  # default
        query_lower = original_query.lower()
        if "jazz" in query_lower:
            style = "jazz"
        elif "blues" in query_lower:
            style = "blues"
        elif "rock" in query_lower:
            style = "rock"
        elif "folk" in query_lower:
            style = "folk"
        elif "electronic" in query_lower or "edm" in query_lower:
            style = "electronic"
        
        # Usar acordes extraídos o generar basados en estilo
        chords = elements.get("chords", [])
        if not chords and style in self.music_knowledge["chord_progressions"]:
            # Usar progresión conocida
            prog_key = list(self.music_knowledge["chord_progressions"][style].keys())[0]
            chords = self.music_knowledge["chord_progressions"][style][prog_key]["chords"]
        
        # Determinar tonalidad
        key = elements.get("key", "C")
        
        # Determinar tempo
        tempo = elements.get("tempo")
        if not tempo:
            tempo_ranges = {
                "ballad": 70, "pop": 120, "rock": 130, "jazz": 110, "blues": 90, "electronic": 128
            }
            tempo = tempo_ranges.get(style, 120)
        
        # Generar estructura completa
        composition = {
            "metadata": {
                "title": f"AI Generated {style.title()} Composition",
                "style": style,
                "key": key,
                "tempo": tempo,
                "time_signature": "4/4",
                "generated_at": datetime.now().isoformat(),
                "ai_model": self.current_model
            },
            "harmonic_structure": {
                "chord_progression": chords,
                "key_center": key,
                "progression_type": self.identify_progression_type(chords),
                "harmonic_rhythm": "1 chord per measure"
            },
            "melodic_guidelines": {
                "recommended_scale": self.suggest_scale(key, style),
                "note_range": f"{key}4-{key}6",
                "melodic_contour": "arch shape preferred",
                "phrase_length": "4 measures"
            },
            "rhythmic_structure": {
                "style": style,
                "groove": self.get_rhythm_pattern(style),
                "tempo": tempo,
                "feel": "straight" if style != "jazz" else "swing"
            },
            "instrumentation": {
                "primary": elements.get("instruments", self.music_knowledge["instrumentation"].get(f"{style}_band", ["piano", "guitar", "drums"])),
                "arrangement_notes": f"Typical {style} arrangement"
            },
            "song_structure": {
                "form": "ABABCB",  # Verse-Chorus-Verse-Chorus-Bridge-Chorus
                "sections": {
                    "A": "Verse - storytelling, lower energy",
                    "B": "Chorus - hook, higher energy", 
                    "C": "Bridge - contrast, often modulates"
                }
            },
            "production_notes": {
                "style_characteristics": self.get_style_characteristics(style),
                "mixing_tips": f"Focus on {style} production techniques",
                "reference_tracks": "TBD based on specific style"
            }
        }
        
        return composition
    
    def identify_progression_type(self, chords: List[str]) -> str:
        """Identificar tipo de progresión"""
        if not chords:
            return "unknown"
        
        chord_str = "-".join(chords)
        
        # Patterns comunes
        if "C-G-Am-F" in chord_str or "I-V-vi-IV" in chord_str:
            return "Pop progression (I-V-vi-IV)"
        elif len(chords) == 3 and "7" in chords[-1]:
            return "Jazz ii-V-I or variation"
        elif len(chords) > 8:
            return "Blues progression (12-bar likely)"
        else:
            return f"{len(chords)}-chord progression"
    
    def suggest_scale(self, key: str, style: str) -> str:
        """Sugerir escala basada en tonalidad y estilo"""
        if style == "jazz":
            return f"{key} mixolydian or dorian"
        elif style == "blues":
            return f"{key} pentatonic minor + blues notes"
        elif style == "folk":
            return f"{key} major pentatonic"
        else:
            return f"{key} major scale"
    
    def get_rhythm_pattern(self, style: str) -> str:
        """Obtener patrón rítmico para el estilo"""
        patterns = {
            "pop": "K-S-K-S (kick on 1&3, snare on 2&4)",
            "rock": "K-S-K-S with hi-hat eighths",
            "jazz": "swing feel, brushes preferred",
            "blues": "shuffle rhythm (triplet feel)",
            "folk": "simple acoustic strumming",
            "electronic": "four-on-the-floor kick pattern"
        }
        return patterns.get(style, patterns["pop"])
    
    def get_style_characteristics(self, style: str) -> List[str]:
        """Obtener características del estilo"""
        characteristics = {
            "pop": ["catchy hooks", "verse-chorus structure", "accessible harmony"],
            "jazz": ["complex harmony", "improvisation", "swing feel"],
            "blues": ["12-bar form", "call-and-response", "blue notes"],
            "rock": ["power chords", "strong backbeat", "guitar-driven"],
            "folk": ["acoustic instruments", "storytelling lyrics", "simple harmony"],
            "electronic": ["synthesized sounds", "programmed drums", "build-ups and drops"]
        }
        return characteristics.get(style, ["genre-appropriate elements"])
    
    async def create_complete_song(self, user_request: str) -> Dict[str, Any]:
        """Crear una canción completa basada en la solicitud del usuario"""
        
        print(f"🎵 Procesando: {user_request}")
        
        # 1. Consultar IA para obtener elementos musicales
        ai_response = await self.query_ollama(user_request)
        
        if not ai_response:
            print("⚠️ IA no disponible, usando generación basada en reglas")
            return self.fallback_generation(user_request)
        
        print(f"🤖 IA Response: {ai_response[:100]}...")
        
        # 2. Extraer elementos musicales
        elements = self.extract_musical_elements(ai_response)
        print(f"🔍 Elementos extraídos: {elements}")
        
        # 3. Generar composición completa
        composition = self.generate_from_elements(elements, user_request)
        
        # 4. Crear resultado final
        result = {
            "user_request": user_request,
            "ai_analysis": ai_response,
            "extracted_elements": elements,
            "generated_composition": composition,
            "graphiti_episode": {
                "name": f"Musical Generation: {user_request[:50]}",
                "content": ai_response,
                "extracted_data": elements,
                "final_composition": composition["metadata"],
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return result
    
    def fallback_generation(self, request: str) -> Dict[str, Any]:
        """Generación de respaldo sin IA"""
        # Lógica básica basada en palabras clave
        style = "pop"
        if "jazz" in request.lower():
            style = "jazz"
        elif "blues" in request.lower():
            style = "blues"
        
        return {
            "user_request": request,
            "ai_analysis": "IA no disponible - generación basada en reglas",
            "generated_composition": {
                "metadata": {
                    "title": "Fallback Composition",
                    "style": style,
                    "key": "C",
                    "tempo": 120
                }
            }
        }


async def demo_complete_system():
    """Demostración del sistema completo"""
    
    print("🎯 SISTEMA COMPLETO DE GENERACIÓN MUSICAL")
    print("=" * 60)
    print("Integración: Ollama + Graphiti + Teoría Musical + AI Platform")
    print()
    
    system = CompleteMusicSystem()
    
    # Casos de prueba
    test_cases = [
        "Crea una balada pop romántica en tonalidad de G mayor a 75 BPM",
        "Genera un tema de jazz bebop uptempo con piano y saxofón",
        "Compón una progresión de blues en Mi para guitarra eléctrica",
        "Diseña una pista electrónica energética a 128 BPM para bailar"
    ]
    
    print("🎼 PROCESANDO SOLICITUDES MUSICALES:")
    print("-" * 40)
    
    for i, request in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {request}")
        print("⏳ Generando...")
        
        try:
            result = await system.create_complete_song(request)
            
            composition = result["generated_composition"]
            metadata = composition["metadata"]
            
            print(f"✅ Generación exitosa!")
            print(f"   🎹 Título: {metadata['title']}")
            print(f"   🔑 Tonalidad: {metadata['key']}")
            print(f"   ⏱️  Tempo: {metadata['tempo']} BPM")
            print(f"   🎭 Estilo: {metadata['style']}")
            
            # Mostrar elementos musicales clave
            harmonic = composition.get("harmonic_structure", {})
            if harmonic.get("chord_progression"):
                chords = " → ".join(harmonic["chord_progression"][:4])  # Primeros 4 acordes
                print(f"   🎼 Acordes: {chords}")
            
            # Mostrar instrumentación
            instrumentation = composition.get("instrumentation", {})
            if instrumentation.get("primary"):
                instruments = ", ".join(instrumentation["primary"][:3])  # Primeros 3 instrumentos
                print(f"   🎸 Instrumentos: {instruments}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ DEMOSTRACIÓN COMPLETADA")
    print("🚀 Sistema listo para integración con AI Music Platform")


if __name__ == "__main__":
    asyncio.run(demo_complete_system())