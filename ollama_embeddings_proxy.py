#!/usr/bin/env python3
"""
Servidor proxy que traduce requests de OpenAI embeddings API a Ollama
Soluciona el problema de que Graphiti intenta usar /v1/embeddings pero Ollama usa /api/embeddings
"""

import asyncio
import json
import logging
from typing import List, Dict, Any

import aiohttp
from aiohttp import web
import requests

# Configuración
OLLAMA_BASE_URL = "http://192.168.100.20:11434"
EMBEDDING_MODEL = "nomic-embed-text"
PROXY_PORT = 11435

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaEmbeddingsProxy:
    def __init__(self):
        self.session = None
    
    async def create_session(self):
        """Crear sesión HTTP async"""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Cerrar sesión HTTP async"""
        if self.session:
            await self.session.close()
    
    async def get_embeddings_from_ollama(self, texts: List[str]) -> List[List[float]]:
        """Obtener embeddings de Ollama para una lista de textos"""
        embeddings = []
        
        for text in texts:
            payload = {
                "model": EMBEDDING_MODEL,
                "prompt": text
            }
            
            try:
                async with self.session.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        embedding = result.get("embedding", [])
                        embeddings.append(embedding)
                        logger.debug(f"Got embedding for text (len={len(text)}): {len(embedding)} dimensions")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama embeddings error {response.status}: {error_text}")
                        # Retornar embedding vacío en caso de error
                        embeddings.append([])
            except Exception as e:
                logger.error(f"Error calling Ollama embeddings: {str(e)}")
                embeddings.append([])
        
        return embeddings

    async def handle_openai_embeddings_request(self, request: web.Request) -> web.Response:
        """Manejar request de embeddings compatible con OpenAI API"""
        try:
            # Parse request body
            body = await request.json()
            logger.info(f"Received embeddings request: {json.dumps(body, indent=2)}")
            
            # Extraer textos del request
            input_data = body.get("input", [])
            if isinstance(input_data, str):
                input_data = [input_data]
            elif not isinstance(input_data, list):
                raise ValueError("Input must be string or list of strings")
            
            # Obtener embeddings de Ollama
            embeddings = await self.get_embeddings_from_ollama(input_data)
            
            # Formato de respuesta compatible con OpenAI
            response_data = {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "index": i,
                        "embedding": embedding
                    }
                    for i, embedding in enumerate(embeddings)
                ],
                "model": EMBEDDING_MODEL,
                "usage": {
                    "prompt_tokens": sum(len(text.split()) for text in input_data),
                    "total_tokens": sum(len(text.split()) for text in input_data)
                }
            }
            
            logger.info(f"Returning {len(embeddings)} embeddings")
            return web.json_response(response_data)
            
        except Exception as e:
            logger.error(f"Error processing embeddings request: {str(e)}")
            return web.json_response(
                {"error": {"message": str(e), "type": "invalid_request_error"}},
                status=400
            )

    async def handle_models_request(self, request: web.Request) -> web.Response:
        """Manejar request de modelos compatible con OpenAI API"""
        response_data = {
            "object": "list",
            "data": [
                {
                    "id": EMBEDDING_MODEL,
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "ollama",
                    "permission": [],
                    "root": EMBEDDING_MODEL,
                    "parent": None
                }
            ]
        }
        return web.json_response(response_data)

async def create_app() -> web.Application:
    """Crear aplicación web"""
    proxy = OllamaEmbeddingsProxy()
    await proxy.create_session()
    
    app = web.Application()
    
    # Rutas compatibles con OpenAI API
    app.router.add_post('/v1/embeddings', proxy.handle_openai_embeddings_request)
    app.router.add_get('/v1/models', proxy.handle_models_request)
    
    # Cleanup
    async def cleanup_context(app):
        yield
        await proxy.close_session()
    
    app.cleanup_ctx.append(cleanup_context)
    
    return app

async def main():
    """Función principal"""
    logger.info(f"Starting Ollama Embeddings Proxy on port {PROXY_PORT}")
    logger.info(f"Proxying to Ollama at {OLLAMA_BASE_URL}")
    logger.info(f"Using embedding model: {EMBEDDING_MODEL}")
    
    app = await create_app()
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PROXY_PORT)
    await site.start()
    
    logger.info(f"Proxy server started on http://0.0.0.0:{PROXY_PORT}")
    logger.info("Routes available:")
    logger.info("  POST /v1/embeddings - OpenAI-compatible embeddings endpoint")
    logger.info("  GET  /v1/models - List available models")
    
    # Mantener el servidor corriendo
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down proxy server...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())