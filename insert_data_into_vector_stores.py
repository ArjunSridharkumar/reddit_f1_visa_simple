from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from generate_embedding import generate_embedding
from insert_data_into_db import extract_post_comments_from_the_pdf
import chromadb
import numpy as np
from chromadb.config import Settings
from chromadb import Client
from chromadb.utils import embedding_functions
# from chromadb.models import Collection
from tqdm import tqdm
import deeplake

# def search_using_milvus(query_embedding,collection):
#     search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
#     results = collection.search([query_embedding], "embedding", param=search_params, limit=3, expr=None)
#     return results

def insert_into_deeplake(pdf_file_name, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS):
    deeplake_cloud_path ="hub://arjunskumar2021/reddit_embeddings_1"
    try:
        print("Extracting posts, comments from the PDF document.")
        posts_dict = extract_post_comments_from_the_pdf(pdf_file_name)
    except Exception as e:
        import pdb; pdb.set_trace()
        raise(e)
        print('extract_post_comments_from_the_pdf failed due to', e)
    deeplake_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpZCI6ImFyanVuc2t1bWFyMjAyMSIsImFwaV9rZXkiOiJBUGhFZFZma2dhYlZKQlU0QUh2bTMzOWVlaHdkOENMR0Z2N2VQTG00MlJreFYifQ."
    # dataset = deeplake.empty('./deeplake_posts', overwrite=True)
    dataset = deeplake.empty(deeplake_cloud_path, token=deeplake_token, overwrite=True)
    dataset.create_tensor('post_id', dtype=str)
    dataset.create_tensor('post_embedding', dtype=np.float32)
    # dataset.create_tensor('comment_id', dtype=str)
    post_counter = 1
    post_to_comment_mapping = {}
    posts_dict = {k: posts_dict[k] for k in list(posts_dict)}
    for key, value in tqdm(posts_dict.items()):
        try:
            post_embedding = generate_embedding(key, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS, False)
        except Exception as e:
            print(e)
            import pdb; pdb.set_trace()

        post_id = str(post_counter)
        dataset.append({
            'post_id': post_id,
            'post_embedding': post_embedding,
        })
        if post_id in post_to_comment_mapping:
            import pdb;pdb.set_trace()
        post_to_comment_mapping[post_id] = value
        post_counter += 1

        # comment_counter = 0
        # for comment in value:
        #     comment_id = f"{post_id}_{comment_counter}"
        #     dataset.append({
        #         'comment_id': comment_id,
        #         'comment_text': comment,
        #         'post_ref': post_id
        #     })
        #     comment_counter += 1



    print("Data successfully inserted into Deep Lake vector store.")
    return post_to_comment_mapping

def insert_into_chroma(pdf_file_name, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS):
    try:
        print("Extracting posts, comments from the PDF document.")
        posts_dict = extract_post_comments_from_the_pdf(pdf_file_name)
    except Exception as e:
        import pdb;pdb.set_trace()
        raise(e)
        print('extract_post_comments_from_the_pdf failed due to', e)
    # import pdb;pdb.set_trace()
    # client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="."))
    posts_dict = {k: posts_dict[k] for k in list(posts_dict)}
    # chroma_client = chromadb.Client()
    chroma_client = chromadb.PersistentClient('./chroma')
    # chroma_client = chromadb.Client(Settings(persist_directory="./chroma", chroma_db_impl="duckdb+parquet"))
    # chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma"))
    existing_collections = chroma_client.list_collections()
    names_collections = [i.name for i in existing_collections]
    if ("posts" in names_collections):
        posts_collection = chroma_client.get_collection(name="posts")
        chroma_client.delete_collection(name='posts')
    if ("comments" in names_collections):
        posts_collection = chroma_client.get_collection(name="comments")
        chroma_client.delete_collection(name='comments')

    # import pdb;pdb.set_trace()
    posts_collection = chroma_client.create_collection(name="posts")
    # comments_collection = chroma_client.create_collection(name="comments")
    post_comment_mapping = {}
    post_counter = 1
    for key, value in tqdm(posts_dict.items()):
        try:
            post_embedding = generate_embedding(key, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS, False)
        except Exception as e:
            print(e)
            import pdb;pdb.set_trace()
        post_id = post_counter
        posts_collection.add(embeddings=[post_embedding], ids=[str(post_id)])
        if post_id  in post_comment_mapping:
            import pdb;pdb.set_trace()
        post_comment_mapping[post_id] = value
        # comment_counter = 0
        # for comment in value:
        #     try:
        #         # comment_embedding = generate_embedding(comment, EMBEDDING_MODEL_NAME, EMBEDDING_MAX_TOKENS, False)
        #         comment_embedding = None
        #     except Exception as e:
        #         print(e)
        #         import pdb;pdb.set_trace()
            # comment_id = str(post_id) + "_" + str(comment_counter)
            # comments_collection.add(embeddings=[comment_embedding], ids=[str(comment_id)],metadatas=[{"post_id": post_id, "comment_text": comment}])
            # comment_counter = comment_counter + 1
        post_counter = post_counter + 1

    print("Data successfully inserted into Chroma vector store.")
    return post_comment_mapping

def insert_into_milvus(pdf_file_name, VECTOR_INDEX_METHOD,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS):
    try:
        print ("Extracting posts, comments from the pdf document.")
        posts_dict = extract_post_comments_from_the_pdf(pdf_file_name)
    except Exception as e:
        import pdb;pdb.set_trace()
        raise(e)
        print ('extract_post_comments_from_the_pdf failed due to e',e)
    posts_dict = {k: posts_dict[k] for k in list(posts_dict)}

    #find the longest comment
    comment_lengths = []
    for key,value in posts_dict.items():
        comment_lengths = comment_lengths + [len(i) for i in value]
    MAX_LENGTH_COMMENT = max(comment_lengths)
    connections.connect("default", host="localhost", port="19530")
    #Using seperate collections for posts and comments
    post_id_field = FieldSchema(name="post_id", dtype=DataType.INT64, is_primary=True, auto_id=True)
    post_comment_field = FieldSchema(name="post_comment_id", dtype=DataType.INT64, is_foreign=True)
    title_body_vector_field = FieldSchema(name="title_body_vector", dtype=DataType.FLOAT_VECTOR, dim=1536)
    comment_id_field = FieldSchema(name="comment_id", dtype=DataType.INT64, is_primary=True, auto_id=True)
    comment_vector_field = FieldSchema(name="comment_vector", dtype=DataType.FLOAT_VECTOR, dim=1536)
    comment_text_field = FieldSchema(name="comment_text", dtype=DataType.VARCHAR, max_length=MAX_LENGTH_COMMENT)

    posts_schema = CollectionSchema(fields=[post_id_field, title_body_vector_field], description="Posts collection")
    comments_schema = CollectionSchema(fields=[comment_id_field, post_comment_field, comment_vector_field,comment_text_field], description="Comments collection")

    # import pdb;pdb.set_trace()
    # import pdb;pdb.set_trace()
    if utility.has_collection("posts"):
        Collection("posts").drop()
    if utility.has_collection("comments"):
        Collection("comments").drop()
    posts_collection = Collection(name="posts", schema=posts_schema)
    comments_collection = Collection(name="comments", schema=comments_schema)

    posts_collection.create_index(field_name="title_body_vector", index_params={"metric_type": "COSINE", "index_type": VECTOR_INDEX_METHOD, "params": {"nlist": 128}})
    comments_collection.create_index(field_name="comment_vector", index_params={"metric_type": "COSINE", "index_type": VECTOR_INDEX_METHOD, "params": {"nlist": 128}})

    # import pdb;pdb.set_trace()
    posts_collection.load()
    comments_collection.load()

    for key,value in tqdm(posts_dict.items()):
        try:
            post_embedding = generate_embedding(key,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS,False)
        except Exception as e:
            print (e)
            import pdb;pdb.set_trace()
        # try:
            # if isinstance(post_embedding, list) and len(post_embedding) == 1536:
        insert_result = posts_collection.insert([[post_embedding]])  # Corrected insertion
        post_id = insert_result.primary_keys[0]
        post_comment_id = post_id
            # else:
            #     raise ValueError(f"Invalid embedding for post: {key}")
        # except Exception as e:
        #     print(f"Error generating or inserting embedding for post '{key}': {e}")
        #     continue
        # cur.execute("INSERT INTO posts (title_content, embedding) VALUES (%s, %s) RETURNING id;",(key, post_embedding))
        # post_id = cur.fetchone()[0]
        post_id = insert_result.primary_keys[0]
        post_comment_id = post_id
        for comment in value:
            comment_embedding = generate_embedding(comment,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS,False)
            comments_collection.insert([[post_comment_id], [comment_embedding], [comment]])

def insert_data_into_vector_stores_main(pdf_file_name,VECTOR_STORE_METHOD,VECTOR_INDEX_METHOD,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS):
    if VECTOR_STORE_METHOD == "MILVUS":
        try:
            insert_into_milvus(pdf_file_name,VECTOR_INDEX_METHOD,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
        except Exception as e:
            raise(e)
            print('insert_into_milvus failed due to ', e)
    elif VECTOR_STORE_METHOD == "DEEPLAKE":
        try:
            post_to_comment_mapping = insert_into_deeplake(pdf_file_name,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
        except Exception as e:
            raise(e)
            print('insert_into_deeplake failed due to ', e)
        return post_to_comment_mapping
    else:
        try:
            post_to_comment_mapping=  insert_into_chroma(pdf_file_name,EMBEDDING_MODEL_NAME,EMBEDDING_MAX_TOKENS)
        except Exception as e:
            # import pdb;pdb.set_trace()
            raise(e)
            print('insert_into_chroma failed due to ', e)
        return post_to_comment_mapping