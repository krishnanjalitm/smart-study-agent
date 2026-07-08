"""
smart-study-agent/backend/app/services/watsonx_client.py
Thin wrapper around the IBM watsonx.ai Python SDK.
Provides a single WatsonxClient instance used by all agents.
"""

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from app.core.config import settings
from app.core.logger import logger


class WatsonxClient:
    """Singleton-style wrapper for IBM watsonx.ai Granite model inference."""

    def __init__(self):
        credentials = Credentials(
            url=settings.WATSONX_URL,
            api_key=settings.WATSONX_API_KEY,
        )
        self._client = APIClient(credentials)
        self._model_id   = settings.GRANITE_MODEL_ID
        self._project_id = settings.WATSONX_PROJECT_ID
        logger.info(f"WatsonxClient initialised → model={self._model_id}")

    def _get_model(
        self,
        max_new_tokens: int = 1024,
        temperature: float  = 0.7,
        top_p: float        = 0.9,
    ) -> ModelInference:
        """Instantiate a ModelInference object with the given parameters."""
        params = {
            GenParams.DECODING_METHOD: DecodingMethods.SAMPLE,
            GenParams.MAX_NEW_TOKENS:  max_new_tokens,
            GenParams.MIN_NEW_TOKENS:  10,
            GenParams.TEMPERATURE:     temperature,
            GenParams.TOP_P:           top_p,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        return ModelInference(
            model_id=self._model_id,
            params=params,
            credentials=Credentials(
                url=settings.WATSONX_URL,
                api_key=settings.WATSONX_API_KEY,
            ),
            project_id=self._project_id,
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 1024,
        temperature: float  = 0.7,
    ) -> str:
        """
        Send *prompt* to Granite and return the generated text.
        Falls back to an error string rather than raising so the app
        degrades gracefully if credentials are missing.
        """
        try:
            model    = self._get_model(max_new_tokens=max_new_tokens, temperature=temperature)
            response = model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as exc:
            logger.error(f"WatsonxClient.generate failed: {exc}")
            return f"[AI Error] {str(exc)}"


# Module-level singleton
watsonx = WatsonxClient()
