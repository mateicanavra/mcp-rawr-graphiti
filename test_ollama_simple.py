#!/usr/bin/env python3
"""
Test simple de conexión Ollama para generación musical
"""

import requests
import json

def test_ollama_connection():
    """Test básico de Ollama"""
    
    print("🔍 Probando conexión a Ollama...")
    
    ollama_url = "http://192.168.100.20:11434"
    
    try:
        # Obtener modelos disponibles
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Conectado a Ollama!")
            print(f"📊 Modelos disponibles:")
            
            for model in models.get('models', []):
                print(f"   • {model['name']} ({model.get('size', 'unknown size')})")
            
            # Encontrar modelo de texto
            text_models = [m['name'] for m in models.get('models', []) if 'embed' not in m['name']]
            
            if text_models:
                model_to_use = text_models[0]
                print(f"\n🎯 Usando modelo: {model_to_use}")
                
                # Test de generación simple
                print("🧪 Probando generación musical simple...")
                
                payload = {
                    "model": model_to_use,
                    "prompt": "Suggest a simple chord progression for a happy pop song in C major. Keep it very short.",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 100  # Limitar respuesta
                    }
                }
                
                print("⏳ Generando respuesta...")
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', '').strip()
                    
                    print("✅ Generación exitosa!")
                    print(f"🎵 Respuesta de IA:")
                    print(f"   {ai_response}")
                    
                    # Crear episodio musical para Graphiti
                    musical_episode = {
                        "name": "Progresión de Acordes Pop Generada por IA",
                        "content": ai_response,
                        "model_used": model_to_use,
                        "query": "chord progression for happy pop song",
                        "timestamp": "2025-07-23"
                    }
                    
                    print(f"\n📊 Episodio musical creado:")
                    print(f"   Título: {musical_episode['name']}")
                    print(f"   Modelo: {musical_episode['model_used']}")
                    print(f"   Contenido: {musical_episode['content'][:100]}...")
                    
                    return musical_episode
                    
                else:
                    print(f"❌ Error en generación: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            else:
                print("❌ No hay modelos de texto disponibles")
                
        else:
            print(f"❌ Error conectando: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return None

if __name__ == "__main__":
    print("🎵 TEST SIMPLE OLLAMA + MÚSICA")
    print("=" * 40)
    
    episode = test_ollama_connection()
    
    if episode:
        print(f"\n✅ TEST EXITOSO")
        print("🔗 Listo para integrar con Graphiti")
    else:
        print(f"\n❌ TEST FALLIDO")
        print("🔧 Revisar configuración de Ollama")