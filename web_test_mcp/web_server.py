import os
import json
import asyncio
from aiohttp import web
import aiohttp
from groq import Groq
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# =========================
# CONFIGURAÇÃO
# =========================
MODEL = "moonshotai/kimi-k2-instruct-0905"
SYSTEM_PROMPT = """
Você é um Agente DevOps Local e Agente de Automação de PC.
Você tem acesso a ferramentas MCP para:
- executar comandos no terminal
- manipular arquivos (ler, escrever, listar)
- controlar mouse e teclado
- trabalhar com Git
- capturar screenshots

Use as ferramentas sempre que necessário.
Explique o que está fazendo de forma clara.
Seja cuidadoso com comandos destrutivos.
Sempre confirme antes de executar operações importantes.
"""

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# MCP Global - mantém uma única conexão
mcp_client_context = None
mcp_session = None
mcp_tools = []

# =========================
# INICIALIZAR MCP GLOBAL
# =========================
async def initialize_mcp():
    """Inicializa a conexão global com o servidor MCP"""
    global mcp_client_context, mcp_session, mcp_tools
    
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_pc_devops_agent.py"]
    )
    
    print("🔌 Conectando ao servidor MCP...")
    
    try:
        mcp_client_context = stdio_client(server_params)
        read_stream, write_stream = await mcp_client_context.__aenter__()
        
        session_context = ClientSession(read_stream, write_stream)
        mcp_session = await session_context.__aenter__()
        await mcp_session.initialize()
        
        # Carregar ferramentas
        tools_response = await mcp_session.list_tools()
        mcp_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools_response.tools
        ]
        
        print(f"✓ MCP inicializado com {len(mcp_tools)} ferramentas")
        return tools_response.tools
        
    except Exception as e:
        print(f"❌ Erro ao inicializar MCP: {e}")
        raise

# =========================
# CLASSE DE SESSÃO
# =========================
class UserSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    async def process_message(self, user_message):
        """Processa mensagem do usuário"""
        self.messages.append({"role": "user", "content": user_message})
        
        max_iterations = 10
        iteration = 0
        tool_executions = []
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Chamar Groq API
                completion = groq_client.chat.completions.create(
                    model=MODEL,
                    messages=self.messages,
                    tools=mcp_tools,
                    temperature=0.2,
                    max_tokens=2048
                )
                
                assistant_msg = completion.choices[0].message
                
                # Processar tool calls
                if assistant_msg.tool_calls:
                    self.messages.append({
                        "role": "assistant",
                        "content": assistant_msg.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_msg.tool_calls
                        ]
                    })
                    
                    # Executar ferramentas
                    for tool_call in assistant_msg.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        try:
                            result = await mcp_session.call_tool(tool_name, tool_args)
                            
                            # Extrair texto do resultado
                            result_text = ""
                            if hasattr(result, 'content'):
                                for content_item in result.content:
                                    if hasattr(content_item, 'text'):
                                        result_text += content_item.text
                            else:
                                result_text = str(result)
                            
                            tool_executions.append({
                                "name": tool_name,
                                "args": tool_args,
                                "result": result_text
                            })
                            
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_text
                            })
                            
                        except Exception as e:
                            error_msg = f"Erro ao executar {tool_name}: {str(e)}"
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg
                            })
                            tool_executions.append({
                                "name": tool_name,
                                "args": tool_args,
                                "result": error_msg
                            })
                    
                    continue
                
                # Resposta final
                else:
                    if assistant_msg.content:
                        self.messages.append({
                            "role": "assistant",
                            "content": assistant_msg.content
                        })
                        return {
                            "content": assistant_msg.content,
                            "tool_executions": tool_executions
                        }
                    break
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "tool_executions": tool_executions
                }
        
        return {
            "content": "Limite de iterações atingido.",
            "tool_executions": tool_executions
        }

# Gerenciamento de sessões de usuário
user_sessions = {}

# =========================
# WEBSOCKET HANDLER
# =========================
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    session_id = str(id(ws))
    session = UserSession(session_id)
    user_sessions[session_id] = session
    
    print(f"✓ Cliente conectado: {session_id}")
    
    try:
        # Enviar lista de ferramentas
        tools_list = [
            {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"]
            }
            for tool in mcp_tools
        ]
        
        await ws.send_json({
            "type": "tools",
            "tools": tools_list
        })
        
        # Enviar mensagem de status
        await ws.send_json({
            "type": "status",
            "message": "Conectado ao servidor MCP"
        })
        
        # Loop de mensagens
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    
                    if data.get("type") == "message":
                        user_message = data.get("content")
                        
                        # Processar mensagem
                        response = await session.process_message(user_message)
                        
                        if "error" in response:
                            await ws.send_json({
                                "type": "error",
                                "message": response["error"]
                            })
                        else:
                            # Enviar execuções de ferramentas
                            for tool_exec in response.get("tool_executions", []):
                                await ws.send_json({
                                    "type": "tool_execution",
                                    "name": tool_exec["name"],
                                    "args": tool_exec["args"],
                                    "result": tool_exec["result"]
                                })
                            
                            # Enviar resposta final
                            await ws.send_json({
                                "type": "response",
                                "content": response.get("content", "")
                            })
                    
                    elif data.get("type") == "clear":
                        session.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                        await ws.send_json({
                            "type": "status",
                            "message": "Histórico limpo"
                        })
                
                except json.JSONDecodeError:
                    await ws.send_json({
                        "type": "error",
                        "message": "Formato de mensagem inválido"
                    })
            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'❌ Erro WebSocket: {ws.exception()}')
    
    except Exception as e:
        print(f"❌ Erro no handler WebSocket: {e}")
    
    finally:
        # Limpar sessão
        if session_id in user_sessions:
            del user_sessions[session_id]
        print(f"✗ Cliente desconectado: {session_id}")
    
    return ws

# =========================
# HTTP HANDLERS
# =========================
async def index_handler(request):
    """Serve a página HTML"""
    html_file = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(html_file):
        return web.FileResponse(html_file)
    else:
        return web.Response(
            text="Arquivo index.html não encontrado. Certifique-se de que está no mesmo diretório.",
            status=404
        )

async def health_handler(request):
    """Endpoint de health check"""
    return web.json_response({
        "status": "ok",
        "sessions": len(user_sessions),
        "mcp_connected": mcp_session is not None,
        "tools_available": len(mcp_tools)
    })

# =========================
# LIFECYCLE
# =========================
async def on_startup(app):
    """Executado ao iniciar o servidor"""
    try:
        await initialize_mcp()
    except Exception as e:
        print(f"❌ Falha ao inicializar MCP: {e}")
        raise

async def on_cleanup(app):
    """Executado ao parar o servidor"""
    global mcp_client_context, mcp_session
    print("\n🛑 Encerrando servidor...")
    
    if mcp_session:
        try:
            await mcp_session.__aexit__(None, None, None)
        except:
            pass
    
    if mcp_client_context:
        try:
            await mcp_client_context.__aexit__(None, None, None)
        except:
            pass

# =========================
# APLICAÇÃO
# =========================
def create_app():
    app = web.Application()
    
    # Lifecycle
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    # Rotas
    app.router.add_get('/', index_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/ws', websocket_handler)
    
    return app

# =========================
# MAIN
# =========================
def main():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erro: GROQ_API_KEY não configurada")
        print("   Execute: export GROQ_API_KEY='sua_chave_aqui'")
        exit(1)
    
    print("🚀 Iniciando servidor web...")
    print("   Interface: http://localhost:8080")
    print("   WebSocket: ws://localhost:8080/ws")
    print("   Health: http://localhost:8080/health")
    print("\nPressione Ctrl+C para parar\n")
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080, print=None)

if __name__ == "__main__":
    main()
