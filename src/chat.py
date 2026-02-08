import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from src.search import search

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        # Note: 'gpt-5-nano' is the requested model name. 
        # If this model is not available, please change to 'gpt-4o-mini' or similar.
        return ChatOpenAI(model="gpt-5-nano") 
    elif os.getenv("GOOGLE_API_KEY"):
        # Note: 'gemini-2.5-flash-lite' is the requested model name.
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
    else:
        raise ValueError("No API key found via OPENAI_API_KEY or GOOGLE_API_KEY")

def format_docs(docs):
    return "\n\n".join([d.page_content for d, score in docs])

def chat_loop():
    print("Iniciando Chat... (Digite 'sair' para encerrar)")
    
    try:
        llm = get_llm()
    except Exception as e:
        print(f"Erro ao inicializar LLM: {e}")
        return

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    while True:
        try:
            user_input = input("\nFaça sua pergunta: ")
            if user_input.lower() in ["sair", "exit", "quit"]:
                break
            
            if not user_input.strip():
                continue

            # Vector Search
            results = search(user_input, k=10)
            context = format_docs(results)
            
            # Generate response
            chain = prompt | llm
            try:
                response = chain.invoke({"context": context, "question": user_input})
                print(f"\nRESPOSTA: {response.content}")
            except Exception as llm_error:
                print(f"\nErro na chamada da LLM: {llm_error}")
                print("Verifique se o modelo solicitado está disponível e se a API Key está correta.")
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    chat_loop()
