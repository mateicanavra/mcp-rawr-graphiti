#!/usr/bin/env python3
"""
Integración entre Ollama, Graphiti y Generación Musical
Combina embeddings de Ollama con conocimiento musical del grafo
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class OllamaMusicIntegration:
    """Integración entre Ollama y el generador musical basado en Graphiti"""
    
    def __init__(self, ollama_host: str = "192.168.100.20", ollama_port: int = 11434):
        self.ollama_url = f"http://{ollama_host}:{ollama_port}"
        self.available_models = []
        self.current_model = None
        
    async def check_ollama_connection(self) -> bool:
        """Verificar conexión con Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                print(f"✅ Conectado a Ollama. Modelos disponibles: {len(self.available_models)}")
                for model in self.available_models:
                    print(f"   • {model}")
                return True
            else:
                print(f"❌ Error conectando a Ollama: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ No se pudo conectar a Ollama: {e}")
            print("💡 Asegúrate de que Ollama esté ejecutándose en 192.168.100.20:11434")
            return False
    
    def set_model(self, model_name: str) -> bool:
        """Establecer el modelo a usar"""
        if model_name in self.available_models:
            self.current_model = model_name
            print(f"🎯 Modelo seleccionado: {model_name}")
            return True
        else:
            print(f"❌ Modelo {model_name} no disponible")
            return False
    
    def select_best_model(self) -> Optional[str]:
        """Seleccionar el mejor modelo disponible para generación de texto"""
        # Priorizar modelos de lenguaje sobre embeddings
        text_models = [model for model in self.available_models if 'embed' not in model]
        if text_models:
            return text_models[0]  # llama3.2:3b
        return self.available_models[0] if self.available_models else None
    
    async def generate_musical_description(self, prompt: str) -> Optional[str]:
        """Generar descripción musical usando Ollama"""
        if not self.current_model:
            best_model = self.select_best_model()
            if best_model:
                self.current_model = best_model
                print(f"🤖 Auto-seleccionando modelo: {self.current_model}")
            else:
                print("❌ No hay modelos disponibles")
                return None
        
        try:
            payload = {
                "model": self.current_model,
                "prompt": f"""Eres un experto en teoría musical y composición. 
                
Consulta: {prompt}

Por favor, responde con información musical específica y práctica. 
Incluye aspectos como:
- Escalas o modos recomendados
- Progresiones de acordes apropiadas  
- Patrones rítmicos sugeridos
- Tempo y mood
- Instrumentación sugerida

Mantén la respuesta concisa pero informativa.""",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"❌ Error en generación: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error generando con Ollama: {e}")
            return None
    
    def parse_musical_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de Ollama para extraer elementos musicales"""
        musical_elements = {
            "scales": [],
            "chords": [],
            "tempo": None,
            "mood": None,
            "style": None,
            "key": None,
            "instruments": [],
            "raw_response": response
        }
        
        # Parsing básico (en un sistema real, sería más sofisticado)
        response_lower = response.lower()
        
        # Detectar escalas y modos
        scales = ['mayor', 'minor', 'pentatonic', 'blues', 'dorian', 'mixolydian', 'lydian']
        for scale in scales:
            if scale in response_lower:
                musical_elements["scales"].append(scale)
        
        # Detectar acordes comunes
        chords = ['c', 'dm', 'em', 'f', 'g', 'am', 'bdim']
        for chord in chords:
            if f" {chord} " in response_lower or f"{chord}-" in response_lower:
                musical_elements["chords"].append(chord.upper())
        
        # Detectar tempo (buscar números seguidos de "bpm")
        import re
        tempo_match = re.search(r'(\d+)\s*bpm', response_lower)
        if tempo_match:
            musical_elements["tempo"] = int(tempo_match.group(1))
        
        # Detectar mood/carácter
        moods = ['happy', 'sad', 'energetic', 'calm', 'dark', 'bright', 'melancholic']
        for mood in moods:
            if mood in response_lower:
                musical_elements["mood"] = mood
                break
        
        return musical_elements
    
    async def enhanced_music_generation(self, user_request: str) -> Dict[str, Any]:
        """Generación musical mejorada usando Ollama + Graphiti"""
        
        print(f"🎵 Procesando solicitud: {user_request}")
        
        # 1. Generar descripción con Ollama
        ollama_response = await self.generate_musical_description(user_request)
        
        if not ollama_response:
            print("⚠️  Usando generación base sin Ollama")
            return self.fallback_generation(user_request)
        
        # 2. Parsear elementos musicales
        musical_elements = self.parse_musical_response(ollama_response)
        
        # 3. Generar música basada en los elementos detectados
        generated_music = self.create_music_from_elements(musical_elements, user_request)
        
        # 4. Agregar respuesta como episodio al grafo
        episode_data = {
            "user_request": user_request,
            "ollama_response": ollama_response,
            "extracted_elements": musical_elements,
            "generated_music": generated_music,
            "timestamp": datetime.now().isoformat(),
            "model_used": self.current_model
        }
        
        return {
            "success": True,
            "user_request": user_request,
            "ai_analysis": ollama_response,
            "musical_elements": musical_elements,
            "generated_composition": generated_music,
            "graph_episode": episode_data
        }
    
    def create_music_from_elements(self, elements: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Crear composición musical basada en elementos extraídos"""
        
        # Determinar tonalidad
        key = elements.get("key", "C")
        if not key:
            # Inferir tonalidad del contexto
            if "happy" in context.lower() or "bright" in context.lower():
                key = "C"  # Mayor
            elif "sad" in context.lower() or "dark" in context.lower():
                key = "Am"  # Menor
            else:
                key = "C"
        
        # Determinar tempo
        tempo = elements.get("tempo", 120)
        if not tempo:
            if "slow" in context.lower() or "ballad" in context.lower():
                tempo = 70
            elif "fast" in context.lower() or "upbeat" in context.lower():
                tempo = 140
            else:
                tempo = 120
        
        # Determinar estilo
        style = "pop"  # Default
        if "jazz" in context.lower():
            style = "jazz"
        elif "blues" in context.lower():
            style = "blues"
        elif "rock" in context.lower():
            style = "rock"
        
        # Generar estructura musical
        composition = {
            "metadata": {
                "title": f"Composición AI: {context[:30]}...",
                "key": key,
                "tempo": tempo,
                "style": style,
                "mood": elements.get("mood", "neutral"),
                "generated_by": "ollama_graphiti_integration",
                "timestamp": datetime.now().isoformat()
            },
            "harmonic_structure": self.generate_chord_progression(style, key),
            "melodic_suggestions": self.generate_melody_outline(elements),
            "rhythmic_pattern": self.generate_rhythm(style, tempo),
            "ai_insights": {
                "recommended_scales": elements.get("scales", ["major"]),
                "suggested_instruments": elements.get("instruments", ["piano", "guitar"]),
                "composition_notes": elements.get("raw_response", "")[:200] + "..."
            }
        }
        
        return composition
    
    def generate_chord_progression(self, style: str, key: str) -> List[str]:
        """Generar progresión de acordes"""
        progressions = {
            "pop": ["I", "V", "vi", "IV"],
            "jazz": ["ii", "V", "I", "vi"],
            "blues": ["I", "IV", "V", "I"],
            "rock": ["vi", "IV", "I", "V"]
        }
        
        return progressions.get(style, progressions["pop"])
    
    def generate_melody_outline(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Generar esquema melódico"""
        return {
            "recommended_scales": elements.get("scales", ["major"]),
            "note_range": "C4-C6",
            "phrase_structure": "AABA",
            "melodic_direction": "ascending" if elements.get("mood") == "happy" else "mixed"
        }
    
    def generate_rhythm(self, style: str, tempo: int) -> Dict[str, Any]:
        """Generar patrón rítmico"""
        patterns = {
            "pop": "K-S-K-S",
            "jazz": "K-x-S-x-K-x-S-x", 
            "blues": "K-x-S-x-K-x-S-x",
            "rock": "K-S-h-S"
        }
        
        return {
            "pattern": patterns.get(style, patterns["pop"]),
            "tempo": tempo,
            "time_signature": "4/4",
            "swing": style in ["jazz", "blues"]
        }
    
    def fallback_generation(self, request: str) -> Dict[str, Any]:
        """Generación de respaldo sin Ollama"""
        return {
            "success": False,
            "message": "Ollama no disponible, usando generación básica",
            "generated_composition": {
                "metadata": {
                    "title": "Composición básica",
                    "key": "C",
                    "tempo": 120,
                    "style": "pop"
                }
            }
        }


async def demo_integration():
    """Demostración de la integración Ollama-Graphiti-Música"""
    
    print("🎯 DEMO: INTEGRACIÓN OLLAMA + GRAPHITI + MÚSICA")
    print("=" * 60)
    
    # Inicializar integración
    integration = OllamaMusicIntegration()
    
    # Verificar conexión
    connected = await integration.check_ollama_connection()
    
    if connected and integration.available_models:
        # Usar el mejor modelo disponible para generación de texto
        best_model = integration.select_best_model()
        if best_model:
            integration.set_model(best_model)
        
        # Ejemplos de solicitudes musicales
        requests = [
            "Crea una balada triste en modo menor para piano",
            "Genera un tema de jazz upbeat con tempo rápido",
            "Compón una progresión de acordes para una canción pop alegre",
            "Sugiere una melodía en escala pentatónica para blues"
        ]
        
        print("\n🎵 PROCESANDO SOLICITUDES MUSICALES:")
        print("-" * 40)
        
        for i, request in enumerate(requests, 1):
            print(f"\n📝 Solicitud {i}: {request}")
            print("⏳ Procesando con Ollama...")
            
            result = await integration.enhanced_music_generation(request)
            
            if result["success"]:
                print(f"✅ Generación exitosa:")
                print(f"   🎹 Tonalidad: {result['generated_composition']['metadata']['key']}")
                print(f"   ⏱️  Tempo: {result['generated_composition']['metadata']['tempo']} BPM")
                print(f"   🎭 Mood: {result['generated_composition']['metadata']['mood']}")
                print(f"   🎼 Estilo: {result['generated_composition']['metadata']['style']}")
                
                # Mostrar insight de IA (primeras líneas)
                ai_insight = result["ai_analysis"][:150] + "..." if len(result["ai_analysis"]) > 150 else result["ai_analysis"]
                print(f"   🤖 IA Insight: {ai_insight}")
            else:
                print("❌ Error en la generación")
    
    else:
        print("\n⚠️  Ollama no disponible - ejecutando demo sin IA")
        print("💡 Para conectar con Ollama:")
        print("   1. Verificar SSH a 192.168.100.20")
        print("   2. Confirmar que Ollama esté ejecutándose")
        print("   3. Verificar puerto 11434")


if __name__ == "__main__":
    asyncio.run(demo_integration())