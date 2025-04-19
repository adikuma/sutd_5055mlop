# BYTEUS Project

## Team Members

- Caitlin Chiang (1006537)
- Aditya Kumar (1006300)
- Chin Wei Ming (1006264)
- Mahima Sharma (1006106)

## Project Description

This project involved creating an advanced chatbot for SUTD prospective students. We fine-tuned a Llama 3.2 1B model on question-answer pairs about SUTD. The project compared multiple approaches:

1. Base model without RAG
2. Fine-tuned model without RAG
3. Base model with RAG
4. Fine-tuned model with RAG

Our results showed that the fine-tuned model with RAG achieved the best performance with a 467% improvement in BLEU scores and 4.6% improvement in cosine similarity compared to the base model.

The project leveraged several technologies:

- LangChain for RAG implementation
- Unsloth for parameter-efficient fine-tuning
- FAISS for vector storage
- Flashrank for reranking
- Google AI Studio with Gemini 2.0 for synthetic data generation

The final evaluation used multiple metrics including BLEU scores, cosine similarity, and an LLM-as-judge evaluation framework that assessed faithfulness, relevance, and completeness of responses.
