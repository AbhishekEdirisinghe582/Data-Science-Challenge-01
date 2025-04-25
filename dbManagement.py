import os
from chromadb.config import Settings
import chromadb

class DBManager:
    def __init__(self, db_directory='./chroma'):
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

        print(f"Using database directory: {os.path.abspath(db_directory)}")
        
        print(f"Using persist directory: {db_directory}")
        self.client = chromadb.PersistentClient(settings=Settings(persist_directory=db_directory))
        self.collection = self.client.get_or_create_collection("documents")

    def insert_data(self, document_data):
        try:
            chunks = document_data['chunks']
            metadata = document_data['metadata']

            if len(chunks) != len(metadata):
                raise ValueError("Number of chunks does not match number of metadata entries.")

            self.collection.add(
                documents=chunks,
                metadatas=metadata,
                ids=[str(item['chunkId']) for item in metadata]
            )
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")

    def retrieve_data(self, query, n_results=5):
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)

            print("Raw Retrieved Results:", results)
            if 'documents' in results and isinstance(results['documents'], list):
                formatted_results = []
                for i in range(min(n_results, len(results['documents'][0]))):
                    document_text = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}

                    formatted_results.append({
                        "chunkId": metadata.get('chunkId', 'N/A'),
                        "page": metadata.get('page', 'N/A'),
                        "section": metadata.get('section', 'N/A'),
                        "text": document_text
                    })

                return formatted_results
            else:
                print("Error: Unexpected results format or missing 'documents'.")
                return []

        except Exception as e:
            print(f"Error retrieving data: {e}")
            return []

    def update_data(self, chunkId, new_text):
        try:
            results = self.collection.get(
                ids=[str(chunkId)],
                include=['metadatas']
            )

            if results and results['ids']:
                if results['ids'][0] == str(chunkId):
                    metadata_to_update = results.get('metadatas', [{}])[0] if results.get('metadatas') and results['metadatas'] else {}
                    self.collection.update(
                        ids=[str(chunkId)],
                        documents=[new_text],
                        metadatas=[metadata_to_update]
                    )
                    print(f"Chunk {chunkId} updated successfully.")
                else:
                    print(f"No document found with chunkId {chunkId}.")
            else:
                print(f"No document found with chunkId {chunkId}.")
        except Exception as e:
            print(f"Error updating data: {e}")

    def delete_data(self, chunkId):
        try:
            self.collection.delete(ids=[str(chunkId)])
            print(f"Chunk {chunkId} deleted successfully.")
        except Exception as e:
            print(f"Error deleting data: {e}")
