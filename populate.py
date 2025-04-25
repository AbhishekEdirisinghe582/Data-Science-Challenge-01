import os
import json
from preprocessor import Preprocessor
from vectorStorage import VectorStore

def main():
    pdf_path = "rawInput/grade-11-history-text-book.pdf"
    output_dir = "preprocessed_data"
    db_directory = './chroma'
    chunk_size = 100

    urls_to_scrape = [
        "https://kids.nationalgeographic.com/history/article/wright-brothers",
        "https://en.wikipedia.org/wiki/Wright_Flyer",
        "https://airandspace.si.edu/collection-objects/1903-wright-flyer/nasm_A19610048000",
        "https://en.wikipedia.org/wiki/Wright_brothers",
        "https://spacecenter.org/a-look-back-at-the-wright-brothers-first-flight/",
        "https://udithadevapriya.medium.com/a-history-of-education-in-sri-lanka-bf2d6de2882c",
        "https://en.wikipedia.org/wiki/Education_in_Sri_Lanka",
        "https://thuppahis.com/2018/05/16/the-earliest-missionary-english-schools-challenging-shirley-somanader/",
        "https://www.elivabooks.com/pl/book/book-6322337660",
        "https://quizgecko.com/learn/christian-missionary-organizations-in-sri-lanka-bki3tu",
        "https://en.wikipedia.org/wiki/Mahaweli_Development_programme",
        "https://www.cmg.lk/largest-irrigation-project",
        "https://mahaweli.gov.lk/Corporate%20Plan%202019%20-%202023.pdf",
        "https://www.sciencedirect.com/science/article/pii/S0016718524002082",
        "https://www.sciencedirect.com/science/article/pii/S2405844018381635",
        "https://www.britannica.com/story/did-marie-antoinette-really-say-let-them-eat-cake",
        "https://genikuckhahn.blog/2023/06/10/marie-antoinette-and-the-infamous-phrase-did-she-really-say-let-them-eat-cake/",
        "https://www.instagram.com/mottahedehchina/p/Cx07O8XMR8U/?hl=en",
        "https://www.reddit.com/r/HistoryMemes/comments/rqgcjs/let_them_eat_cake_is_the_most_famous_quote/",
        "https://www.history.com/news/did-marie-antoinette-really-say-let-them-eat-cake",
        "https://encyclopedia.ushmm.org/content/en/article/adolf-hitler-early-years-1889-1921",
        "https://en.wikipedia.org/wiki/Adolf_Hitler",
        "https://encyclopedia.ushmm.org/content/en/article/adolf-hitler-early-years-1889-1913",
        "https://www.history.com/articles/adolf-hitler",
        "https://www.bbc.co.uk/teach/articles/zbrx8xs"
    ]

    print("Starting preprocessing of PDF and URLs...")
    preprocessor = Preprocessor(pdf_path, output_dir, chunk_size)
    all_chunks, all_metadata = preprocessor.preprocess_and_store(urls_to_scrape)

    print(f"Preprocessing complete. {len(all_chunks)} chunks created and saved to {output_dir}/chunksWithMetadata.json.")

    print("Initializing VectorStore and storing data...")
    vector_storage = VectorStore(db_directory)
    if len(all_chunks) == len(all_metadata):
        vector_storage.insert(all_chunks, all_metadata)
        print("Data successfully stored in Chroma database.")
    else:
        raise ValueError(f"Number of chunks ({len(all_chunks)}) does not match number of metadata entries ({len(all_metadata)}).")

if __name__ == "__main__":
    main()