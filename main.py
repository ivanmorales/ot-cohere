from llama_index.core import VectorStoreIndex
from llama_index.llms.cohere import Cohere
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.postprocessor.cohere_rerank import CohereRerank
from dotenv import load_dotenv
from llama_index.readers.file import HTMLTagReader
import os
from pathlib import Path
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import StorageContext, load_index_from_storage

from utils import should_reindex

import click

DOCS_DIR = "docs"
STORE_DIR = "store"

load_dotenv()
cohere_api_key = os.environ.get('COHERE_API_KEY') #keep your api key in the .env file and retrieve it

model = "command" #this is the model name from cohere. Select it that matches with you 
temperature = 0 # It can be range from (0-1) as openai
max_tokens = 256 # token limit
Settings.llm = Cohere(model=model,temperature=0,api_key=cohere_api_key,max_tokens=max_tokens) #
Settings.embed_model = CohereEmbedding(model_name='embed-english-light-v2.0',cohere_api_key=cohere_api_key)

Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
Settings.num_output = 512
Settings.context_window = 3900


if should_reindex(docs=DOCS_DIR, store=STORE_DIR):
  # rebuild storage context
  storage_context = StorageContext.from_defaults(persist_dir=Path(STORE_DIR))
  # load index
  index = load_index_from_storage(storage_context)
else:
  reader = HTMLTagReader(tag="section", ignore_no_id=True)
  docs = []
  for file in Path(DOCS_DIR).rglob('*'):
    docs.extend(reader.load_data(file))

  index = VectorStoreIndex.from_documents(
          docs, show_progress=True)

  index.storage_context.persist(persist_dir=Path(STORE_DIR))

cohere_rerank = CohereRerank(api_key=cohere_api_key, top_n=3)

query_engine = index.as_query_engine(
  node_postprocessors = [cohere_rerank]
)

@click.command()
@click.option('--question', prompt="Ask me anything")
def query(question):
  click.secho('____________________', fg="green")
  click.secho(query_engine.query(question), fg="red")

  query()

if __name__ == '__main__':
  query()