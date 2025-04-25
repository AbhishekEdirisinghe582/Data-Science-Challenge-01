import os
import dotenv
from vectorStorage import VectorStore
from RAG import RAG
from references import ReferenceManager

def main():
    dotenv.load_dotenv()
    db_directory = './chroma'
    similarity_threshold = 0.9
    print("Initializing vector storage...")
    vector_storage = VectorStore(db_directory)

    print("Setting up RAG pipeline with Gemini...")
    rag = RAG(model="gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

    reference_manager = ReferenceManager("references.json")

    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        print(f"Query: {query}")

        context_results = vector_storage.search(query)

        similar_context = [
            item for item in context_results if item["score"] <= similarity_threshold
        ]
        context_texts = [item["text"] for item in similar_context]
        formatted_context = "\n".join(context_texts)
        print(f"Context retrieved (filtered): {formatted_context}")
        references_to_save = None
        if not similar_context:
            response_text = rag.query_gemini("", query)
            print(f"Response: {response_text}")
        else:

            response_text = rag.query_gemini(formatted_context, query)
            print(f"Response: {response_text}")

            sections = set()
            pages = set()
            for item in similar_context:
                if "section" in item:
                    sections.add(item["section"])
                if "page" in item:
                    pages.add(str(item["page"]))

            references_to_save = {
                "sections": sorted(list(sections)),
                "pages": sorted(list(pages))
            }
        if references_to_save != None and (references_to_save["sections"] or references_to_save["pages"]):
            reference_manager.save_references(references_to_save)
            if references_to_save != None:
                print('sections')
                for i in references_to_save.get('sections'):
                    print(i)
                print('pages')
                for i in references_to_save.get('pages'):
                    print(i)
            else:
                print('references: None')
        else:
            print("No relevant sections or pages found in the context.")

if __name__ == "__main__":
    main()