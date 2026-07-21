"""Creates (once) and reuses the OpenAI-backed support assistant.

The knowledge base PDF is uploaded to an OpenAI vector store and searched via the
`file_search` tool on every call to the Responses API — this is the current OpenAI-recommended
replacement for the (deprecated) Assistants/Threads API, while keeping the same idea: one
persistent knowledge base, reused across runs instead of re-uploaded every time.

Run directly to (re)create the vector store and print its id:
    python assistant_manager.py
"""

from pathlib import Path

from dotenv import set_key
from openai import OpenAI

from config import Settings, get_settings
from templates import SUPPORT_ASSISTANT_SYSTEM_PROMPT

ENV_PATH = Path(".env")


class SupportAssistant:
    """Owns the OpenAI client and the knowledge-base vector store, and answers questions from it."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self._vector_store_id = self.settings.vector_store_id

    @property
    def _vector_stores(self):
        # Older openai SDK versions expose this under the `beta` namespace.
        return getattr(self.client, "vector_stores", None) or self.client.beta.vector_stores

    def _vector_store_exists(self, vector_store_id: str) -> bool:
        try:
            self._vector_stores.retrieve(vector_store_id)
            return True
        except Exception:
            return False

    def ensure_vector_store(self) -> str:
        """Return a ready-to-use vector store id, reusing the configured one when possible."""
        if self._vector_store_id and self._vector_store_exists(self._vector_store_id):
            return self._vector_store_id

        if not self.settings.knowledge_base_file.exists():
            raise FileNotFoundError(
                f"Knowledge base file not found: {self.settings.knowledge_base_file}"
            )

        vector_store = self._vector_stores.create(name=self.settings.vector_store_name)

        with self.settings.knowledge_base_file.open("rb") as f:
            self._vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=f)

        if ENV_PATH.exists():
            set_key(str(ENV_PATH), "VECTOR_STORE_ID", vector_store.id)

        self._vector_store_id = vector_store.id
        return vector_store.id

    def ask(self, question: str, previous_response_id: str | None = None):
        """Ask the support bot a question, scoped strictly to the knowledge base."""
        vector_store_id = self._vector_store_id or self.ensure_vector_store()

        return self.client.responses.create(
            model=self.settings.assistant_model,
            instructions=SUPPORT_ASSISTANT_SYSTEM_PROMPT,
            input=question,
            tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
            previous_response_id=previous_response_id,
        )


if __name__ == "__main__":
    vs_id = SupportAssistant().ensure_vector_store()
    print(f"Vector store ready: {vs_id}")
