import random
from app.config.setting import settings

class EmbeddingManager:
    def fake_embed(self, text: str) -> list:
        """
        Generate deterministic fake embedding based on input text hash.
        """
        random.seed(abs(hash(text)) % 10000)
        return [random.random() for _ in range(settings.VECTOR_SIZE)]

# Global instance
embedding_manager = EmbeddingManager()