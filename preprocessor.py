import fitz
import re
import json
import os
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import requests

class Preprocessor:
    def __init__(self, pdfPath=None, outputDir="preprocessed_data", chunkSize=100):
        self.pdfPath = pdfPath
        self.outputDir = outputDir
        self.chunkSize = chunkSize
        self.chunks = []
        self.metadata = []
        self.global_chunk_id = 0

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def scrape_text_from_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            article_content = soup.find('article')
            if not article_content:
                article_content = soup.find('div', {'class': 'article-body'})
            if not article_content:
                article_content = soup.find('main')
            if not article_content:
                article_content = soup.find('body')

            if article_content:
                text = article_content.get_text(separator='\n', strip=True)
                return self.clean_text(text)
            else:
                print(f"Warning: Could not find main content for URL: {url}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None
        except Exception as e:
            print(f"Error processing content from {url}: {e}")
            return None

    def chunk_and_annotate_text(self, text, source_url):
        text_chunks = []
        metadata_list = []
        sentences = sent_tokenize(text)
        current_chunk = ""

        for sentence in sentences:
            if len(word_tokenize(current_chunk + " " + sentence)) <= self.chunkSize:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    text_chunks.append(current_chunk.strip())
                    metadata_list.append({
                        "chunkId": self.global_chunk_id,
                        "source": source_url,
                        "section": source_url,
                        "text": current_chunk.strip()
                    })
                    self.global_chunk_id += 1
                current_chunk = sentence.strip()

        if current_chunk.strip():
            text_chunks.append(current_chunk.strip())
            metadata_list.append({
                "chunkId": self.global_chunk_id,
                "source": source_url,
                "section": source_url,
                "text": current_chunk.strip()
            })
            self.global_chunk_id += 1 

        return text_chunks, metadata_list

    def process_pdf(self):
        self.chunks = []
        self.metadata = []
        doc = fitz.open(self.pdfPath)
        current_section = ""
        current_page = 1

        for page_num in range(len(doc)):
            page_text = doc.load_page(page_num).get_text().splitlines()
            current_content_in_section = ""

            for line in page_text:
                page_number_match = re.match(r'^\s*-\s*(\d+)\s*-?\s*$', line)
                if page_number_match:
                    current_page = int(page_number_match.group(1))
                    print(f"  >> Page Number Found (PDF): {current_page}")
                    continue

                section_match = re.match(r'^\s*\d+\.\d+(\.\s+)?\s*.+$', line) or re.match(r'^\s*\s*.+$', line)
                if section_match:
                    current_section = line.strip()
                    print(f"  >> Section Found (PDF): '{current_section}'")
                    continue

                if line.strip():
                    sentences = sent_tokenize(line)
                    for sentence in sentences:
                        temp_content = (current_content_in_section + " " + sentence).strip()
                        if len(word_tokenize(temp_content)) <= self.chunkSize - len(word_tokenize(current_section)) - 5:
                            current_content_in_section = temp_content
                        else:
                            if current_content_in_section:
                                chunk_text = f"{current_section}. {current_content_in_section}"
                                self.chunks.append(chunk_text)
                                self.metadata.append({
                                    "chunkId": self.global_chunk_id,
                                    "page": current_page,
                                    "section": current_section,
                                    "source": self.pdfPath,
                                    "text": chunk_text
                                })
                                self.global_chunk_id += 1
                                current_content_in_section = sentence.strip()

            if current_content_in_section.strip():
                chunk_text = f"{current_section}. {current_content_in_section}"
                self.chunks.append(chunk_text)
                self.metadata.append({
                    "chunkId": self.global_chunk_id,
                    "page": current_page,
                    "section": current_section,
                    "source": self.pdfPath,
                    "text": chunk_text
                })
                self.global_chunk_id += 1 

        return self.chunks, self.metadata

    def process_urls(self, urls):
        all_url_chunks = []
        all_url_metadata = []
        for url in urls:
            print(f"Processing URL: {url}")
            text = self.scrape_text_from_url(url)
            if text:
                chunks, metadata = self.chunk_and_annotate_text(text, url)
                all_url_chunks.extend(chunks)
                all_url_metadata.extend(metadata)
        return all_url_chunks, all_url_metadata

    def saveChunksAndMetadata(self, chunks, metadata):
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        outputPath = os.path.join(self.outputDir, 'chunksWithMetadata.json')
        with open(outputPath, 'w') as f:
            json.dump({"chunks": chunks, "metadata": metadata}, f, indent=4)

    def preprocess_and_store(self, urls=None):
        all_chunks = []
        all_metadata = []
        self.global_chunk_id = 0

        if self.pdfPath:
            pdf_chunks, pdf_metadata = self.process_pdf()
            all_chunks.extend(pdf_chunks)
            all_metadata.extend(pdf_metadata)

        if urls:
            url_chunks, url_metadata = self.process_urls(urls)
            all_chunks.extend(url_chunks)
            all_metadata.extend(url_metadata)


        if len(all_chunks) == len(all_metadata):
            updated_metadata = []
            for i, meta in enumerate(all_metadata):
                updated_metadata.append({**meta, "chunkId": i})
            self.chunks = all_chunks
            self.metadata = updated_metadata
        else:
            raise ValueError("Number of chunks and metadata do not match after processing.")

        self.saveChunksAndMetadata(self.chunks, self.metadata)
        print(f"Preprocessing complete. {len(self.chunks)} chunks created and saved to {os.path.join(self.outputDir, 'chunksWithMetadata.json')}.")
        return self.chunks, self.metadata