from typing import Optional

from ..utils.logger import logger
from .base_provider import BaseProvider

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception as exc:
    GEMINI_AVAILABLE = False
    genai = None
    _GEMINI_IMPORT_ERROR = str(exc)


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = 'gemini-2.5-flash', endpoint: Optional[str] = None):
        super().__init__(api_key=api_key, model=model, endpoint=endpoint)
        self.enabled = GEMINI_AVAILABLE and bool(api_key)

        if self.enabled:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        else:
            self.client = None
            error_details = f" ({_GEMINI_IMPORT_ERROR})" if '_GEMINI_IMPORT_ERROR' in globals() else ''
            logger.warning(f'Gemini provider unavailable (missing package, incompatible runtime, or API key){error_details}')

    def generate_conversion(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError('Gemini provider is not initialized')

        import time
        import random
        
        max_retries = 3  # Reduced from 5 for faster failure recovery
        base_delay = 1   # Start at 1 second, not 10 (much faster!)

        for attempt in range(max_retries):
            try:
                response = self.client.generate_content(prompt)
                return (response.text or '').strip()
            except Exception as e:
                error_str = str(e).lower()
                if '429' in error_str or 'quota' in error_str or 'exhausted' in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter for better recovery
                        sleep_time = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                        logger.warning(
                            f"Gemini Rate Limit/Quota hit (attempt {attempt + 1}/{max_retries}). "
                            f"Waiting {sleep_time:.1f}s before retry..."
                        )
                        time.sleep(sleep_time)
                        continue
                    else:
                        # After retries exhausted, fail with helpful message
                        logger.error(f"Gemini rate limit exhausted after {max_retries} attempts")
                        raise RuntimeError(
                            f"Gemini API rate limit exceeded after {max_retries} retries. "
                            "Please try again in a few moments."
                        )
                raise
