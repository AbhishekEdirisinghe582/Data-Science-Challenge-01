# references.py
import os
import json

class ReferenceManager:
    def __init__(self, ref_file="references.json"):
        self.ref_file = ref_file
        self.references = self.load_references()

    def load_references(self):
        if os.path.exists(self.ref_file):
            with open(self.ref_file, "r") as file:
                return json.load(file)
        return {}

    def save_references(self, references_data):
        with open(self.ref_file, "w") as file:
            json.dump(references_data, file, indent=4)

    def add_reference(self, chunk_id, reference_data):
        if chunk_id not in self.references:
            self.references[chunk_id] = []
        
        self.references[chunk_id].append(reference_data)
        self.save_references()

    def get_references(self, chunk_id):
        return self.references.get(chunk_id, [])

    def update_reference(self, chunk_id, old_reference, new_reference):
        if chunk_id in self.references:
            try:
                index = self.references[chunk_id].index(old_reference)
                self.references[chunk_id][index] = new_reference
                self.save_references()
            except ValueError:
                print(f"Reference not found for chunk_id {chunk_id}")
        else:
            print(f"No references found for chunk_id {chunk_id}")

    def delete_reference(self, chunk_id, reference_data):
        if chunk_id in self.references:
            try:
                self.references[chunk_id].remove(reference_data)
                self.save_references()
            except ValueError:
                print(f"Reference not found for chunk_id {chunk_id}")
        else:
            print(f"No references found for chunk_id {chunk_id}")
