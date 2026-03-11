from pypdf import PdfReader
from langchain_community.vectorstores import Chroma

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


from langchain_text_splitters import RecursiveCharacterTextSplitter
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, 
        chunk_overlap = 200
    )
    return splitter.split_text(text)
#isme splitter ka kya mtlab hai?The `splitter` in the code refers to an instance of the `RecursiveCharacterTextSplitter` class from the `langchain.text_splitter` module. This class is used to split a large text into smaller chunks based on specified parameters.


from langchain_community.embeddings import HuggingFaceEmbeddings
embedding = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)


from langchain_community.vectorstores import Chroma


def create_vector_store(chunks):
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embedding,
        persist_directory="./db"
    )
    vectorstore.persist()