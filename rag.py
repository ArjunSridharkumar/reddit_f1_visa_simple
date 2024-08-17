# import psycopg2
import chromadb
import os
from sklearn.metrics.pairwise import cosine_similarity
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import openai
import numpy
from chromadb import Client
from chromadb.config import Settings
import deeplake
# from chromadb.models import Collection
# from generate_embedding import generate_embedding
# def rag_using_postgres(query_embedding):
#     top_posts = None
#     relevant_comments = []
#     conn = psycopg2.connect(
#         dbname="reddit_db_1",
#         user="codespace",
#         password="your_new_password",
#         host="localhost",
#         port="5432"
#     )
#     cur = conn.cursor()
#     query_vector = f"[{','.join(map(str, query_embedding))}]"
#     cur.execute(f"""
#         SELECT id, title_content, embedding <=> '{query_vector}'::vector AS distance
#         FROM posts
#         ORDER BY distance DESC
#         LIMIT 10;
#     """)
#     top_posts = cur.fetchall()
#     if (top_posts is not None):
#         # import pdb;pdb.set_trace()
#         # print (top_posts)
#         pass
#     elif len(top_posts) < 1:
#         print ("top posts cannot be retrieved for RAG")
#         import pdb;pdb.set_trace()
#     else:
#         print ("top posts cannot be retrieved for RAG")
#         import pdb;pdb.set_trace()

#     post_ids_list = [i[0] for i in top_posts]
#     if len(post_ids_list):
#         for post_id in post_ids_list:
#             cur.execute("""
#                          SELECT content from comments where post_id = %s;""", (post_id,))
#             relevant_comments.extend([row[0] for row in cur.fetchall()])
#     else:
#         print ("top post ids cannot be retrieved for RAG")
#         import pdb;pdb.set_trace()

#     if len(relevant_comments):
#         return relevant_comments
#     else:
#         print ("relevant comments cannot be retrieved for RAG")
#         import pdb;pdb.set_trace()
#         return None
def rag_using_deeplake(query_embedding,post_comment_mapping):
    relevant_comments = []
    dataset = deeplake.load('./deeplake_posts')
    post_ids_list = []
    for i, post in enumerate(dataset):
        post_embedding = post['post_embedding'].numpy()
        similarity = cosine_similarity(post_embedding,query_embedding)[0][0]
        post_ids_list.append((post['post_id'].numpy(), similarity))
    post_ids_list.sort(key=lambda x: x[1], reverse=True)
    top_post_ids = [post_id for post_id, _ in post_ids_list[:10]]
    for post_id_value in top_post_ids:
        relevant_comments.append(post_comment_mapping[post_id_value])
    if relevant_comments is not None:
        return relevant_comments
    else:
        print("Relevant comments cannot be retrieved for RAG.")
        import pdb; pdb.set_trace()
        return None
    # pass

def rag_using_chroma(query_embedding,post_comment_mapping):
    # import pdb;pdb.set_trace()
    relevant_comments = []
    chroma_client = chromadb.PersistentClient("./chroma")
    # client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="."))
    # print ("list collection", chroma_client.list_collection())
    print ("list collection",chroma_client.list_collections())
    
    import os
    print (os.listdir())
    posts_collection = chroma_client.get_collection("posts")
    # comments_collection = client.get_collection("comments")
    search_results = posts_collection.query(query_embeddings=[query_embedding], n_results=10)
    for result in search_results['ids'][0]:
        # import pdb;pdb.set_trace()
        post_id = result
        # comments = comments_collection.query(where={"post_id": post_id}, include=["comment_text"])
        # for comment in comments['documents']:
        #     relevant_comments.append(comment['comment_text'])
        relevant_comments.append(post_comment_mapping[post_id])
    if relevant_comments:
        return relevant_comments
    else:
        print("Relevant comments cannot be retrieved for RAG.")
        import pdb;pdb.set_trace()
        return None
def rag_using_milvus(query_embedding):
    relevant_comments = []
    connections.connect("default", host="localhost", port="19530")
    posts_collection = Collection('posts')
    comments_collection = Collection('comments')
    posts_collection.load()
    comments_collection.load()
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    results = posts_collection.search([query_embedding], "title_body_vector", search_params, limit=10)
    print (len(results))
    for result in results:
        post_id = result.ids[0]
        # print(f"Post ID: {post_id}")
        expr = f"post_comment_id == {post_id}"
        comments = comments_collection.query(expr=expr,output_fields=['comment_text'])
        # comments = comments_collection.query(f"post_id == {post_id}")
        # print(f"Post ID: {post_id}")
        for comment in comments:
            # print(f"Comment: {comment}")
            relevant_comments.append(comment['comment_text'])
            # import pdb;pdb.set_trace()
    if len(relevant_comments):
        return relevant_comments
    else:
        print ("relevant comments cannot be retrieved for RAG")
        import pdb;pdb.set_trace()
        return None


def rag_main_func(query_embedding,rag_type,VECTOR_INDEX_METHOD,post_comment_mapping):
    if rag_type=="PGVECTOR":
        relevant_comments = rag_using_postgres(query_embedding)
    elif rag_type=="MILVUS":
        relevant_comments = rag_using_milvus(query_embedding)
    elif rag_type == "CHROMA":
        try:
            relevant_comments = rag_using_chroma(query_embedding,post_comment_mapping)
        except Exception as e:
            print(e)
    elif rag_type == "DEEPLAKE":
        relevant_comments = rag_using_deeplake(query_embedding, post_comment_mapping)
    else:
        print ("RAG TYPE method is incorrect.")
        return None
    return relevant_comments
# query = "How can I renew my visa under OPT?"
# query_embedding =  generate_embedding(query, "text-embedding-3-small", 8191)
# model_name = 'text-embedding-3-small'
# MAX_TOKENS = 8191

# try:
#     relevant_comments = rag_main_func(query_embedding,"MILVUS","HNSW")
# except Exception as e:
#     print ('rag_main_func failed due to ', e)
