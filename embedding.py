import numpy as np
from rdflib import Graph
from sentence_transformers import SentenceTransformer, util
import torch

# Load pre-trained sentence embeddings model (for embedding-based answers)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load the precomputed embeddings from the .npy file (these are embeddings for the possible answers)
embedding_file_path = 'embedding.npy'  # Replace with the path to your embedding.npy file
precomputed_embeddings = np.load(embedding_file_path)

# Load the list of possible answers corresponding to these embeddings (you may need to load them from a file as well)
possible_answers = ["Richard Marquand", "George Lucas", "Francis Ford Coppola", "Cengiz Küçükayvaz"]  # Example list, replace with actual list

# Initialize RDFLib graph (SPARQL-based Knowledge Graph)
g = Graph()
g.parse("path_to_your_knowledge_graph.rdf")  # Replace with actual knowledge graph file

# Function to perform SPARQL query
def sparql_query(query):
    try:
        result = g.query(query)
        return list(result)
    except Exception as e:
        print(f"Error running SPARQL query: {e}")
        return None

# Function to get factual answer from Knowledge Graph
def get_factual_answer(question):
    # Convert question to a SPARQL query (you would need to customize these mappings)
    if "director of" in question.lower():
        entity = question.split("director of")[-1].strip().replace("?", "")
        sparql = f"""
        SELECT ?director WHERE {{
            ?movie rdf:type dbo:Film ;
                   rdfs:label "{entity}"@en ;
                   dbo:director ?director .
        }}
        """
        result = sparql_query(sparql)
        if result:
            return result[0][0]  # First director from result
        return "No factual answer found."
    
    if "screenwriter of" in question.lower():
        entity = question.split("screenwriter of")[-1].strip().replace("?", "")
        sparql = f"""
        SELECT ?screenwriter WHERE {{
            ?movie rdf:type dbo:Film ;
                   rdfs:label "{entity}"@en ;
                   dbo:writer ?screenwriter .
        }}
        """
        result = sparql_query(sparql)
        if result:
            return result[0][0]  # First screenwriter from result
        return "No factual answer found."
    
    if "released" in question.lower():
        entity = question.split("released")[-1].strip().replace("?", "")
        sparql = f"""
        SELECT ?releaseDate WHERE {{
            ?movie rdf:type dbo:Film ;
                   rdfs:label "{entity}"@en ;
                   dbo:releaseDate ?releaseDate .
        }}
        """
        result = sparql_query(sparql)
        if result:
            return result[0][0]  # First release date from result
        return "No factual answer found."
    
    return "Unsupported factual question."

# Function to get embedding-based answer
def get_embedding_answer(question):
    # Embedding the question
    question_embedding = model.encode(question, convert_to_tensor=True)
    
    # Convert precomputed embeddings to tensor
    precomputed_embeddings_tensor = torch.tensor(precomputed_embeddings)

    # Compute similarity between question embedding and precomputed answer embeddings
    similarities = util.pytorch_cos_sim(question_embedding, precomputed_embeddings_tensor)[0]
    
    # Find the best match
    best_answer_idx = torch.argmax(similarities)
    
    # Return the corresponding answer from the list of possible answers
    return possible_answers[best_answer_idx]

# Main function to get both factual and embedding answers
def get_both_answers(question):
    factual_answer = get_factual_answer(question)
    print(f"Factual Answer: {factual_answer}")
    
    embedding_answer = get_embedding_answer(question)
    print(f"Embedding Answer: {embedding_answer} (Embedding Answer)")

# Example usage
questions = [
    "Who is the director of Star Wars: Episode VI - Return of the Jedi?",
    "Who is the screenwriter of The Masked Gang: Cyprus?",
    "When was The Godfather released?"
]

for q in questions:
    print(f"Question: {q}")
    get_both_answers(q)
    print("\n")
