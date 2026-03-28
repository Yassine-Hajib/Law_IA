# Tec Used 
Embedding : 
	To transform the Text into vector that will be stored on chroma_db we used a model named bgemodel .

Data → Embedding Model → vectors

-> Every Embedding Model is trained on an industry such as Ecommerce Medical ,Law … 

BGE = BAAI General Embedding 
  → The Version used : BAAI/bge-small-en

To use this model we need a class for a python Library  which facilitate the work  named sentencetransformer  It take text
👉 Sends it through a pretrained transformer model
👉 Returns a vector (embedding)


It contain 2 incoder :
→ byencoder : encode the document alone and the query alone and shearch for similarity its fast not accurate
→ Crosse encoder : encode the doc and query in one time its slow but accurate



Chromadb :
   → A Database where the Vectors will Be Stored 
