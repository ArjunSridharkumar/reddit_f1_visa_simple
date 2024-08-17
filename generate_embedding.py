import tiktoken
import os
import openai
from sentence_transformers import SentenceTransformer
from transformers import  AutoTokenizer
def generate_embedding(text,model_name,MAX_TOKENS,query_embedding_bool):
    api_key = os.getenv("OPEN_API_KEY")
    # import pdb;pdb.set_trace()
    try:
        # import pdb;pdb.set_trace()

        if model_name != "dunzhang/stella_en_1.5B_v5":
            tokenizer = tiktoken.encoding_for_model(model_name)
        else:
            tokenizer = AutoTokenizer.from_pretrained('dunzhang/stella_en_1.5B_v5')
        tokens = tokenizer.encode(text)
        #to handle truncation.
        if len(tokens) > MAX_TOKENS:
            tokens = tokens[:MAX_TOKENS]
        truncated_text = tokenizer.decode(tokens)

        # Create the embedding using the model
        if model_name != "dunzhang/stella_en_1.5B_v5":
            openai.api_key = api_key
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=truncated_text,

            )
            embedding = response.data[0].embedding
            # print ("embedding",len(embedding))
            return embedding
        else:

            model = SentenceTransformer("dunzhang/stella_en_1.5B_v5")
            if query_embedding_bool:
                embedding = model.encode(text, prompt_name='s2p_query')
            else:
                embedding = model.encode(text)
            print ("embedding",len(embedding))
            return embedding
        # else:
        #     import pdb;pdb.set_trace()
    except Exception as e:
        raise(e)