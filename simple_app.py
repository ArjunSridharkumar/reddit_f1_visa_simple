
import streamlit as st
from read_parameters import load_parameters
from generate_embedding import generate_embedding
# from insert_data_into_db import insert_into_db_main
from download_reddit_posts import download_data_main
from insert_data_into_vector_stores import insert_data_into_vector_stores_main
from rag import rag_main_func
from llm_question import llm_question_main
from langchain.memory import ConversationBufferMemory
import json

# Load parameters
try:
    parameters = load_parameters("simple_list_of_parameters.txt")
except Exception as e:
    st.error(f"Failed to load parameters: {e}")
    st.stop()

EMBEDDING_MODEL_NAME = parameters['EMBEDDING_MODEL_NAME']
# EMBEDDING_MAX_TOKENS = int(parameters['EMBEDDING_MAX_TOKENS'])
# PROMPT_ENGG_METHOD = parameters['PROMPT_ENGG_METHOD']
VECTOR_STORE_METHOD = parameters['VECTOR_STORE_METHOD']
VECTOR_INDEX_METHOD = parameters['VECTOR_INDEX_METHOD']
LLM_MODEL_NAME = parameters['LLM_MODEL_NAME']
POSTGRES_DB_NAME=parameters['POSTGRES_DB_NAME']
POSTGRES_DB_USER=parameters['POSTGRES_DB_USER']
POSTGRES_DB_PASSWORD=parameters['POSTGRES_DB_PASSWORD']
POSTGRES_DB_HOST=parameters['POSTGRES_DB_HOST']
POSTGRES_DB_PORT=parameters['POSTGRES_DB_PORT']
pdf_file_name="reddit_posts_top_new.pdf"
# Streamlit UI elements
st.title("LLM App with Streamlit")
# st.sidebar.header("Configuration")

# Display and update parameters
# embedding_model = st.sidebar.selectbox('Embedding Model:', ['gpt-4', 'dunzhang/stella_en_1.5B_v5'], index=0)
# vector_store_method = st.sidebar.selectbox('Vector Store Method:', ['POSTGRESQL', 'MILVUS', 'CHROMA'], index=0)
# vector_index_method = st.sidebar.selectbox('Vector Index Method:', ['IVF_FLAT', 'HSNF'], index=0)
# llm_model_name = st.sidebar.selectbox('LLM Model name:', ['GPT-4', 'microsoft/Phi-3-Medium-4K-Instruct'], index=0)
# prompt_engg_method = st.sidebar.selectbox('Prompt Engg Technique:', ['REACT', 'COT'], index=0)

# EMBEDDING_MODEL_NAME = embedding_model
# VECTOR_STORE_METHOD = vector_store_method
# VECTOR_INDEX_METHOD = vector_index_method
# LLM_MODEL_NAME = llm_model_name
# # PROMPT_ENGG_METHOD = prompt_engg_method
EMBEDDING_MODEL_NAME = "gpt-4"
VECTOR_STORE_METHOD = "CHROMA"
if EMBEDDING_MODEL_NAME == "gpt-4":
    EMBEDDING_MAX_TOKENS = 8191
else:
    EMBEDDING_MAX_TOKENS = 131072

# if VECTOR_STORE_METHOD == "MILVUS" or VECTOR_STORE_METHOD == "CHROMA":
#     try:
#         print ("Calling insert_data_into_vector_stores_main for chroma or milvus")
#         insert_data_into_vector_stores_main(pdf_file_name,VECTOR_STORE_METHOD,VECTOR_INDEX_METHOD,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
#     except Exception as e:
#         print ("insert_data_into_vector_stores failed due to ", e)
# else:
#     print ("Calling insert_into_db_main for posgres")
#     try:
#         insert_into_db_main(pdf_file_name,POSTGRES_DB_NAME,POSTGRES_DB_USER,POSTGRES_DB_PASSWORD,POSTGRES_DB_HOST,POSTGRES_DB_PORT,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
#     except Exception as e:
#         print ("insert_into_db_main failed due to ", e)


# if st.sidebar.button("Run Embedding Generation"):
#     st.write("Running Embedding Generation...")
#     generate_embedding(parameters)
#     st.success("Embedding generation complete.")

# if st.sidebar.button("Insert Data into PostGresDB"):
#     st.write("Inserting data into the database...")
#     insert_into_db_main(parameters)
#     st.success("Data inserted into the database.")

# if st.sidebar.button("Insert Data into MilVus Vector Stores"):s
#     st.write("Inserting data into vector stores...")
#     insert_data_into_vector_stores_main(parameters)
#     st.success("Data inserted into vector stores.")

with open('post_comment_mapping.json', 'r') as json_file:
    post_comment_mapping = json.load(json_file)

query = st.text_area("Enter your query:")
memory = ConversationBufferMemory()
if st.button("Ask the LLM"):
    print ("creating the embedding for the query.")
    try:
        query_embedding = generate_embedding(query, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS,True)
    except Exception as e:
        print ("query_generate_embedding failed sdue to ", e)

    #Based on the query, get search results
    print ("Based on the query, get search results.")
    try:
        context = rag_main_func(query_embedding,VECTOR_STORE_METHOD,VECTOR_INDEX_METHOD,post_comment_mapping)
    except Exception as e:
        print ("rag_main_func failed due to ", e)

    #Get the answer from the LLM.
    print ("Get the answer from the LLM")
    try:
        response = llm_question_main(query,context,LLM_MODEL_NAME)
    except Exception as e:
        raise(e)
        print ("llm_question_main failed due to ", e)
    # print ("Response: ",response)
    st.write("Processing your query...")
    # response = llm_question_main(query, parameters)
    st.write(f"LLM Response: {response}")
    st.write("Conversation History:")
    st.write(memory.chat_memory())

