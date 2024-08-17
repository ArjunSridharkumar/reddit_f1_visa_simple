import fitz
import re
import openai
import os
import chromadb
from chromadb.config import Settings


def extract_text_from_pdf(pdf_path):
    with fitz.Document(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def preprocess_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def tokenize_or_chunk_text(processed_text):
    return processed_text.split(". ")

def store_embeddings(processed_text):
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chromadb_data"))
    collection = client.get_or_create_collection(name='pdf_content')
    try:
        text_chunks = tokenize_or_chunk_text(processed_text)
    except Exception as e:
        print ('tokenize_or_chunk_text failed due to', e)
    for i, chunk in enumerate(text_chunks):
        try:
            embedding = generate_embedding(chunk)
        except Exception as e:
            print ('generate_embedding failed due to', e)
        collection.add(
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[{"source": "reddit_posts_with_comments.pdf"}],
        ids=[f"chunk_{i}"]
    )

def query_model(messages):
    client = openai.OpenAI()
    # prompt=f"{context}\n\nUser: {prompt}\nAI:",
    response =  client.chat.completions.create(
      model="gpt-4",
      messages = messages,
      max_tokens=150,
      temperature=0.7
    #   top_p=1.0,
    #   frequency_penalty=0.0,
    #   presence_penalty=0.0,
    #   stop=["User:", "AI:"]
    )
    print (response)
    import pdb;pdb.set_trace()
    return response.choices[0].message.content.strip()


# Example usage
try:
    pdf_text = extract_text_from_pdf('reddit_posts.pdf')
except Exception as e:
    print ("extract_text_from_pdf failed due to ", e)
try:
    processed_text = preprocess_text(pdf_text)
except Exception as e:
    print ("preprocess_text failed due to ", e)
try:
    embedding = store_embeddings(processed_text)
except Exception as e:
    print ("store_embeddings failed due to ", e)


context = processed_text
messages = [
    {"role": "system", "content": "You are a helpful assistant tasked with the responsibility of answering F1 Visa related queries using the context"},
    {"role": "user", "content": f"The context is: {context}"}
]
response = query_model(messages)



# def chat_with_pdf_model():
#     context = processed_text[:2000]  # You can extend this with more context if needed
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         response = query_model(user_input, context)
#         print(f"AI: {response}")

# chat_with_pdf_model()