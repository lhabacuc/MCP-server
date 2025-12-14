import os
import json
import asyncio
from groq import Groq
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import readline
# =========================
# CONFIG
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

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


async def main():
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_pc_devops_agent.py"]
    )
    
    print("Conectando ao servidor MCP...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools_response = await session.list_tools()
            print("\n🔧 Ferramentas MCP disponíveis:")
            for tool in tools_response.tools:
                print(f"  ✓ {tool.name}: {tool.description}")
            print()
            
            # Converter ferramentas MCP para formato Groq
            groq_tools = [
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
            
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            
            print("Agente MCP (Groq + LLaMA) iniciado")
            print("Digite 'exit' ou 'quit' para sair")
            print("Digite 'clear' para limpar histórico\n")
            
            while True:
                user_input = input("(I)EEE> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ("exit", "quit"):
                    print("\nBye...")
                    break
                
                if user_input.lower() == "clear":
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    print("Histórico limpo\n")
                    continue
                
                messages.append({"role": "user", "content": user_input})
                
                # Loop de iteração do agente
                max_iterations = 10
                iteration = 0
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    try:
                        completion = groq_client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            tools=groq_tools,
                            temperature=0.2,
                            max_tokens=2048
                        )
                    except Exception as e:
                        print(f"\n❌ Erro na API Groq: {e}")
                        break
                    
                    assistant_msg = completion.choices[0].message
                    
                    # =========================
                    # PROCESSAR TOOL CALLS
                    # =========================
                    if assistant_msg.tool_calls:
                        # Adicionar mensagem do assistente
                        messages.append({
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
                        
                        # Executar cada ferramenta
                        for tool_call in assistant_msg.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"\n🛠️  Executando: {tool_name}")
                            print(f"    Parâmetros: {json.dumps(tool_args, indent=2, ensure_ascii=False)}")
                            
                            try:
                                result = await session.call_tool(tool_name, tool_args)
                                
                                # Extrair texto do resultado
                                result_text = ""
                                if hasattr(result, 'content'):
                                    for content_item in result.content:
                                        if hasattr(content_item, 'text'):
                                            result_text += content_item.text
                                else:
                                    result_text = str(result)
                                
                                # Limitar tamanho da saída exibida
                                display_result = result_text[:500]
                                if len(result_text) > 500:
                                    display_result += f"\n... (mais {len(result_text) - 500} caracteres)"
                                
                                print(f"    ✓ Resultado: {display_result}")
                                
                                # Adicionar resultado ao histórico
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": result_text
                                })
                                
                            except Exception as e:
                                error_msg = f"Erro ao executar {tool_name}: {str(e)}"
                                print(f"    ✗ {error_msg}")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": error_msg
                                })
                        
                        # Continuar o loop para processar os resultados
                        continue
                    
                    # =========================
                    # RESPOSTA FINAL
                    # =========================
                    else:
                        if assistant_msg.content:
                            print(f"\n🤖 {assistant_msg.content}\n")
                            messages.append({
                                "role": "assistant",
                                "content": assistant_msg.content
                            })
                        break
                
                if iteration >= max_iterations:
                    print("\n⚠️  Limite de iterações atingido\n")

# ENTRYPOINT
if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("Erro: GROQ_API_KEY não configurada")
        print("  Execute: export GROQ_API_KEY='sua_chave_aqui'")
        exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAgente encerrado pelo usuário")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
