## m365client/handlers/embeddings.py

import torch 
import tempfile
import safetensors
from transformers import BertTokenizer, BertModel

def embeddings_to_safetensors(embeddings):
    embeddings_tensor = torch.tensor(embeddings)
    tensors_dict = {"embeddings": embeddings_tensor}
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        safetensors.torch.save_file(tensors_dict, temp_file.name)
        
        with open(temp_file.name, "rb") as file:
            safetensors_bytes = file.read()
    
    return safetensors_bytes

def generate_embeddings(text_chunks):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    embeddings = []
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
            embeddings.append(embedding)
    return embeddings