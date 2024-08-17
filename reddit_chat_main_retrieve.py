from read_parameters import load_parameters
from generate_embedding import generate_embedding
from insert_data_into_db import insert_into_db_main
from download_reddit_posts import download_data_main
from insert_data_into_vector_stores import insert_data_into_vector_stores_main
from rag import rag_main_func
from llm_question import llm_question_main
import json
#Reading all the necessary parameters.
try:
    parameters = load_parameters("simple_list_of_parameters.txt")
except Exception as e:
    raise(e)
    import pdb;pdb.set_trace()
EMBEDDING_MODEL_NAME = parameters['EMBEDDING_MODEL_NAME']
# EMBEDDING_MAX_TOKENS = int(parameters['EMBEDDING_MAX_TOKENS'])
VECTOR_STORE_METHOD = parameters['VECTOR_STORE_METHOD']
VECTOR_INDEX_METHOD = parameters['VECTOR_INDEX_METHOD']
LLM_MODEL_NAME = parameters['LLM_MODEL_NAME']
POSTGRES_DB_NAME=parameters['POSTGRES_DB_NAME']
POSTGRES_DB_USER=parameters['POSTGRES_DB_USER']
POSTGRES_DB_PASSWORD=parameters['POSTGRES_DB_PASSWORD']
POSTGRES_DB_HOST=parameters['POSTGRES_DB_HOST']
POSTGRES_DB_PORT=parameters['POSTGRES_DB_PORT']
pdf_file_name="reddit_posts_top_new.pdf"
# print (parameters)
if EMBEDDING_MODEL_NAME != "dunzhang/stella_en_1.5B_v5":
    EMBEDDING_MAX_TOKENS = 8191
else:
    EMBEDDING_MAX_TOKENS = 131072

# getting the data from reddit api
# print ("getting the data from reddit api")
# try:
#     download_data_main(5000)
# except Exception as e:
#     print ("download_data_main failed due to ", e)

# Inserting data into vector stores.
# print ("Inserting data into vector stores.")
# if VECTOR_STORE_METHOD == "MILVUS" or VECTOR_STORE_METHOD == "CHROMA" or VECTOR_STORE_METHOD == "DEEPLAKE":
#     try:
#         print ("Calling insert_data_into_vector_stores_main for chroma or milvus")
#         post_comment_mapping = insert_data_into_vector_stores_main(pdf_file_name,VECTOR_STORE_METHOD,VECTOR_INDEX_METHOD,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
#     except Exception as e:
#         print ("insert_data_into_vector_stores failed due to ", e)
# else:
#     print ("Calling insert_into_db_main for posgres")
#     try:
#         insert_into_db_main(pdf_file_name,POSTGRES_DB_NAME,POSTGRES_DB_USER,POSTGRES_DB_PASSWORD,POSTGRES_DB_HOST,POSTGRES_DB_PORT,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
#     except Exception as e:
#         print ("insert_into_db_main failed due to ", e)

# print (post_comment_mapping)
# with open('post_comment_mapping.json', 'w') as json_file:
#     json.dump(post_comment_mapping, json_file, indent=4)

with open('post_comment_mapping.json', 'r') as json_file:
    post_comment_mapping = json.load(json_file)

# import pdb;pdb.set_trace()

query = """I have an appointment at the Mumbai vac tomorrow.
I am concerned regarding the traffic. How early should I be present?"""
#creating the embedding for the query.
print ("creating the embedding for the query.")
print (EMBEDDING_MODEL_NAME)
try:
    query_embedding = generate_embedding(query, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS,True)
except Exception as e:
    print ("query_generate_embedding failed due to ", e)

#Based on the query, get search results
print ("Based on the query, get search results.")
try:
    context = rag_main_func(query_embedding,VECTOR_STORE_METHOD,VECTOR_INDEX_METHOD,post_comment_mapping)
except Exception as e:
    print ("rag_main_func failed due to ", e)
print (context)
#Get the answer from the LLM.
print ("Get the answer from the LLM")
try:
    response = llm_question_main(query,context,LLM_MODEL_NAME)
except Exception as e:
    raise(e)
    print ("llm_question_main failed due to ", e)
print ("Response: ",response)

# query = ""


#     search_results = elastic_search(query)
#     # print (search_results)
#     prompt_value = build_prompt(query, search_results)
#     print (prompt_value)
#     answer_1 = llm_response(prompt_value)
#     return answer_1


# rag('How to setup docker')