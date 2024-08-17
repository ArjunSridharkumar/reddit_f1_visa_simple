from datetime import datetime, timezone
import psycopg2
from transformers import AutoTokenizer
from generate_embedding import generate_embedding
import os
import openai
import fitz
from tqdm import tqdm
import re
# import tiktoken


# def generate_embedding(text,model_name,MAX_TOKENS):
#     # Initialize the tokenizer for the specific model
#     tokenizer = tiktoken.encoding_for_model(model_name)

#     # Tokenize the text
#     tokens = tokenizer.encode(text)

#     # Truncate the text if it exceeds the token limit
#     if len(tokens) > MAX_TOKENS:
#         tokens = tokens[:MAX_TOKENS]

#     # Decode tokens back to text
#     truncated_text = tokenizer.decode(tokens)

#     # Generate the embedding using OpenAI's API
#     response = openai.embeddings.create(
#         model="text-embedding-3-small",
#         input=truncated_text
#     )
#     embedding = response.data[0].embedding

#     return embedding


# def generate_embedding_gpt(text,model_name,MAX_TOKENS):
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     # response = openai.embeddings.create(
#     #     model="text-embedding-3-small",
#     #     input=text
#     # )

#     encoded_input = tokenizer(text, return_tensors='pt', truncation=True, max_length=MAX_TOKENS, padding=True)
#     return response.data[0].embedding


def extract_post_comments_from_the_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    posts_pattern = r"Title of the post:(.*?)(?=Title of the post:|\Z)"
    posts = re.findall(posts_pattern, text, re.DOTALL)
    posts_dict = {}
    for post_value in tqdm(posts):
        #Get title and body
        title_to_body_pattern = r"(.*?)(?=Comment of the post: |\Z)"
        title_to_body = re.findall(title_to_body_pattern, post_value, re.DOTALL)
        try:
            title_to_body = title_to_body[0]
        except Exception as e:
            import pdb;pdb.set_trace()
        # if len(title_to_body) > 1:
        #     import pdb;pdb.set_trace()
        #Get comments - outputs as a string.
        list_of_comments = []
        comments_to_title_pattern = r"Comment of the post:(.*?)(?=Title of the post:|\Z)"
        comments = re.findall(comments_to_title_pattern, post_value, re.DOTALL)

        #Get individual comments
        if len(comments) > 0:
            individual_comments_pattern = r"New Comment: (.*?)(?=New Comment: |\Z)"
            individual_comments = re.findall(individual_comments_pattern,comments[0], re.DOTALL)
        list_of_comments = [i for i in individual_comments if len(i) > 0]
        # if len(individual_comments) > 0:
        #     import pdb;pdb.set_trace()
        if title_to_body in posts_dict.keys():
            import pdb;pdb.set_trace()

        posts_dict[title_to_body] = list_of_comments
    return posts_dict
    # posts = text.split("Title of the post: \n.*.Title of the post: \n")[1:]  # Split by post title indicator


    # print (posts)

# Example usage
def store_into_db(posts_dict,conn,cur,embedding_model_name,MAX_TOKENs):
    for key,value in tqdm(posts_dict.items()):
        post_embedding = generate_embedding(key,embedding_model_name,MAX_TOKENs,False)
        # try:
        #     post_embedding = generate_embedding(key,embedding_model_name,MAX_TOKENs)
        # except Exception as e:
        #     # print ('generate_embedding failed due to', e)
        #     import pdb;pdb.set_trace()
        #     raise(e)
            # import pdb;pdb.set_trace()

        # import pdb;pdb.set_trace()
        cur.execute("INSERT INTO posts (title_content, embedding) VALUES (%s, %s) RETURNING id;",(key, post_embedding))
        post_id = cur.fetchone()[0]
        for comment in value:
            comment_embedding = generate_embedding(comment,embedding_model_name,MAX_TOKENs,False)
            cur.execute(
                        "INSERT INTO comments (post_id, content, embedding) VALUES (%s, %s, %s);",
                        (post_id, comment, comment_embedding)
                    )
    conn.commit()

# def extract_and_store_in_db(pdf_path,conn,cur):
#     with fitz.Document(pdf_path) as doc:
#         text = ""
#         for page in doc:
#             text += page.get_text()

#     post_sections = text.split("Title of the posts: \n")
#     import pdb;pdb.set_trace()

#     for section in tqdm(post_sections):
#         lines = section.split("\n")
#         if lines:
#             title = lines[0].strip()
#             post_content = []
#             comments = []
#             is_comment = False

#             for line in lines[1:]:
#                 if "Comments of the post: \n" in line:
#                     is_comment = True
#                 if is_comment:
#                     comments.append(line.strip())
#                 else:
#                     post_content.append(line.strip())

#             # Insert post into the database
#             post_text = " ".join(post_content)
#             try:
#                 post_embedding = generate_embedding(post_text)
#             except Exception as e:
#                 print (e)
#                 import pdb;pdb.set_trace()
#             cur.execute(
#                 "INSERT INTO posts (title, content, embedding) VALUES (%s, %s, %s) RETURNING id;",
#                 (title, post_text, post_embedding)
#             )
#             post_id = cur.fetchone()[0]

#             # Insert comments into the database
#             for comment in comments:
#                 comment_embedding = generate_embedding(comment)
#                 cur.execute(
#                     "INSERT INTO comments (post_id, content, embedding) VALUES (%s, %s, %s);",
#                     (post_id, comment, comment_embedding)
#                 )

#     conn.commit()


def insert_into_db_main(pdf_file_name,dbname,user,password,host,port,embedding_model_name,MAX_TOKENS):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    posts_dict = None
    try:
        print ("Extracting posts, comments from the pdf document.")
        posts_dict = extract_post_comments_from_the_pdf(pdf_file_name)
    except Exception as e:
        print ('extract_post_comments_from_the_pdf (insert_data_into_db) failed due to ', e)
    posts_dict = {k: posts_dict[k] for k in list(posts_dict)}
    if posts_dict is not None:
        try:
            store_into_db(posts_dict,conn,cur,embedding_model_name,MAX_TOKENS)
        except Exception as e:
            raise(e)
    cur.close()
    conn.close()