import json
import os
from dotenv import load_dotenv
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_ingestion import QdrantIngestion


# -----------------------
# Load environment
# -----------------------

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

KNOWLEDGE_FILE = Path(__file__).parent / "farming_knowledge_06_v2.json"
PROMPTS_FILE = Path(__file__).parent / "prompts_06.json"


# -----------------------
# VECTOR STORE
# -----------------------

class SimpleVectorStore:

    def __init__(self, knowledge_path: Path | None = None):

        self.collection_name = "farming_docs"

        self.ingestion = QdrantIngestion(collection_name=self.collection_name)

        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        if knowledge_path:
            self.ingestion.load_and_ingest(knowledge_path, self.encoder)


    def search(self, query: str, n_results: int = 3) -> list:

        query_vector = self.encoder.encode(query).tolist()

        results = self.ingestion.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=n_results
        )

        return [
            {
                "content": hit.payload["content"],
                "metadata": hit.payload["metadata"],
                "distance": hit.score,
            }
            for hit in results.points
        ]


# -----------------------
# LLM Provider
# -----------------------

class LLMProvider:

    def __init__(self, prompts: dict):

        self.prompts = prompts

        from langchain_openai import ChatOpenAI

        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
        )


    def generate(self, question: str, context: str) -> str:

        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=self.prompts["system_prompt"]),
            HumanMessage(
                content=self.prompts["human_prompt_template"].format(
                    context=context,
                    question=question
                )
            )
        ]

        response = self.llm.invoke(messages)

        return response.content


# -----------------------
# RAG PIPELINE
# -----------------------

class RAGPipeline:

    def __init__(
        self,
        knowledge_path=KNOWLEDGE_FILE,
        prompts_path=PROMPTS_FILE,
    ):

        self.prompts = self._load_json(prompts_path)

        self.vectorstore = SimpleVectorStore(knowledge_path=knowledge_path)

        self.llm = LLMProvider(prompts=self.prompts)


    def _load_json(self, path: Path) -> dict | list:

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


    def query(self, question: str, n_results: int = 3) -> dict:

        results = self.vectorstore.search(question, n_results=n_results)

        context_parts = []
        sources = []

        for i, result in enumerate(results, 1):

            context_parts.append(f"Source[{i}]: {result['content']}")

            sources.append(
                {
                    "source_id": i,
                    "crop": result["metadata"].get("crop"),
                    "topic": result["metadata"].get("topic"),
                    "relevance_score": round(result.get("distance", 0), 4),
                }
            )

        context = "\n\n".join(context_parts)

        answer = self.llm.generate(question, context)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "num_sources_used": len(sources),
        }