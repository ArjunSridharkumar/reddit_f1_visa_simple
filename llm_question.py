import re
import openai
import os
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms import OpenAI, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain import HuggingFacePipeline

memory = ConversationBufferMemory()
def build_prompt(query,context):
    prompt_template = """
    You are an F1 visa expert and an immigration consultant. The CONTEXT contains relevant information.
    Answer the QUESTION based on the CONTEXT.
    If the CONTEXT does not contain the answer, give a concise answer.
    Question: {question}

    CONTEXT: {context}
    """.strip()
    context_value_list = []
    for context_value in context:
        context_value_list =context_value_list + [i for i in context_value]
    try:
        context = " ".join(context_value_list)
    except Exception as e:
        import pdb;pdb.set_trace()
    prompt = prompt_template.format(question =query, context = context).strip()
    return prompt

def llm_model_gpt(prompt):
    api_key =os.getenv("OPEN_API_KEY")
    # client = openai.OpenAI()
    openai.api_key = api_key
    # import pdb;pdb.set_trace()
    response = openai.chat.completions.create(
        model = 'gpt-4',
        messages = [{"role":"user","content":prompt}])
    memory.save_context({"user": prompt}, {"AI": response.choices[0].message.content})
    return response.choices[0].message.content

def llm_model_open_source(prompt):
    model_name = "microsoft/Phi-3-Medium-4K-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=16,
        temperature=0.1,
        top_p=0.9,
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    response = llm(prompt)
    return response

def llm_question_main(query,context,LLM_MODEL_NAME):
    # past_interactions = " ".join([f"{msg['role']}: {msg['content']}" for msg in memory.chat_memory.messages])
    # context += " " + past_interactions
    prompt = build_prompt(query,context)
    if LLM_MODEL_NAME != "microsoft/Phi-3-Medium-4K-Instruct":
        response = llm_model_gpt(prompt)
    else:
        response = llm_model_open_source(prompt)
    # memory.save_context({"user": query}, {"AI": response})
    return response

# context = processed_text
# messages = [
#     {"role": "system", "content": "You are a helpful assistant tasked with the responsibility of answering F1 Visa related queries using the context"},
#     {"role": "user", "content": f"The context is: {context}"}
# ]
# response = query_model(messages)





# def extract_text_from_pdf(pdf_path):
#     with fitz.Document(pdf_path) as doc:
#         text = ""
#         for page in doc:
#             text += page.get_text()
#     return text

# def preprocess_text(text):
#     text = text.replace('\n', ' ')
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

# def generate_embedding(text):
#     response = openai.Embedding.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return response['data'][0]['embedding']

# def tokenize_or_chunk_text(processed_text):
#     return processed_text.split(". ")

# def store_embeddings(processed_text):
#     client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chromadb_data"))
#     collection = client.get_or_create_collection(name='pdf_content')
#     try:
#         text_chunks = tokenize_or_chunk_text(processed_text)
#     except Exception as e:
#         print ('tokenize_or_chunk_text failed due to', e)
#     for i, chunk in enumerate(text_chunks):
#         try:
#             embedding = generate_embedding(chunk)
#         except Exception as e:
#             print ('generate_embedding failed due to', e)
#         collection.add(
#         documents=[chunk],
#         embeddings=[embedding],
#         metadatas=[{"source": "reddit_posts_with_comments.pdf"}],
#         ids=[f"chunk_{i}"]
#     )

# def query_model(messages):
#     client = openai.OpenAI()
#     # prompt=f"{context}\n\nUser: {prompt}\nAI:",
#     response =  client.chat.completions.create(
#       model="gpt-4",
#       messages = messages,
#       max_tokens=150,
#       temperature=0.7
#     #   top_p=1.0,
#     #   frequency_penalty=0.0,
#     #   presence_penalty=0.0,
#     #   stop=["User:", "AI:"]
#     )
#     print (response)
#     import pdb;pdb.set_trace()
#     return response.choices[0].message.content.strip()




# def chat_with_pdf_model():
#     context = processed_text[:2000]  # You can extend this with more context if needed
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         response = query_model(user_input, context)
#         print(f"AI: {response}")

# chat_with_pdf_model()
