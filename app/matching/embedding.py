from sentence_transformers import SentenceTransformer

#Load the model only once when the application starts
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    """
    Generate an embedding for the given text using the pre-loaded model.
    """
    if not text:
        text = ""
    embedding = model.encode(text)
    return embedding
