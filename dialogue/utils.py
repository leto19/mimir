from sentence_transformers import SentenceTransformer, util

embedder = SentenceTransformer('bert-base-nli-mean-tokens')

def embedding_cos_sim(user_utterance, comp_str):
    utterance_embedding = embedder.encode(user_utterance, convert_to_tensor=True)
    comp_embedding = embedder.encode(comp_str, convert_to_tensor=True)

    cos_scores = util.pytorch_cos_sim(utterance_embedding, comp_embedding)[0]
    cos_scores = cos_scores.cpu()
    print("Similarity rating: ", cos_scores)
    return cos_scores