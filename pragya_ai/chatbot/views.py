from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from .rag_utils import embedding
from .models import AboutData
from .rag_utils import extract_text_from_pdf, chunk_text, create_vector_store
import json


# Custom prompt to improve chatbot answers
prompt_template = """
You are an AI assistant that answers questions about Pragya Ladha.

Use ONLY the information provided in the context to answer the question.

Important rules:
- Do NOT say phrases like "according to the provided context".
- Answer naturally like a human assistant.
- If the answer is not present in the context, say: "I couldn't find that information."

Context:
{context}

Question:
{question}

Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)


def home(request):
    chat_history = request.session.get("chat_history", [])
    answer = None

    if request.method == "POST":
        question = request.POST.get("question")

        chat_history.append({"sender": "user", "text": question})

        try:
            vectorstore = Chroma(
                persist_directory="./db",
                embedding_function=embedding
            )

            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 6, "fetch_k": 12}
            )

            # llm = ChatOllama(model="llama3")
            llm = ChatOllama(
                model="llama3",
                base_url="http://127.0.0.1:11434"
                )

            qa = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT}
            )

            answer = qa.run(question)

        except Exception as e:
            # answer = "Something went wrong while generating the answer."
            answer = str(e)

        chat_history.append({"sender": "assistant", "text": answer})

        request.session["chat_history"] = chat_history
        request.session.modified = True

    return render(request, "chat.html", {
        "chat_history": chat_history,
        "answer": answer
    })


@csrf_exempt
@require_POST
def chat_api(request):
    """AJAX endpoint for chat messages"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        # Add user message to session
        chat_history = request.session.get("chat_history", [])
        chat_history.append({"sender": "user", "text": question})

        try:
            vectorstore = Chroma(
                persist_directory="./db",
                embedding_function=embedding
            )

            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 6, "fetch_k": 12}
            )

            llm = ChatOllama(model="llama3")

            qa = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT}
            )

            answer = qa.run(question)

        except Exception as e:
            # answer = "Something went wrong while generating the answer."

                answer = str(e)

        # Add assistant message to session
        chat_history.append({"sender": "assistant", "text": answer})
        request.session["chat_history"] = chat_history
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'answer': answer,
            'user_message': question
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)


def upload_data(request):

    if request.method == "POST":
        file = request.FILES["file"]

        obj = AboutData.objects.create(file=file)

        text = extract_text_from_pdf(obj.file.path)

        chunks = chunk_text(text)

        create_vector_store(chunks)

        return redirect("home")

    return render(request, "upload.html")