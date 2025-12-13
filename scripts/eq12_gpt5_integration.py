#!/usr/bin/env python3
"""
EQ12 GPT-5 Integration Module
Centralized GPT-5 functionality for the entire EQ12 system
"""

import base64
import os

try:
    import openai

    GPT5_AVAILABLE = True
except ImportError:
    GPT5_AVAILABLE = False


class EQ12GPT5Integration:
    """Centralized GPT-5 integration for EQ12 system"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if GPT5_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def generate_frontend(self, prompt: str, filename: str = "generated.html") -> str:
        """Generate frontend using GPT-5 patterns"""
        if not self.client:
            return self._fallback_html(prompt)

        try:
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt,
            )
            return response.output_text
        except Exception:
            return self._fallback_html(prompt)

    def analyze_multimodal(
            self,
            text_prompt: str,
            image_path: str | None = None) -> str:
        """Analyze with both text and image input"""
        if not self.client or not image_path:
            return f"Analysis: {text_prompt}"

        try:
            encoded_image = self._encode_image(image_path)
            input_data = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": text_prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{encoded_image}",
                        },
                    ],
                }
            ]

            response = self.client.responses.create(
                model="gpt-5",
                input=input_data,
            )
            return response.output_text
        except Exception as e:
            return f"Multimodal analysis error: {e}"

    def _encode_image(self, image_path: str) -> str:
        """Encode image for GPT-5 input"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _fallback_html(self, prompt: str) -> str:
        """Fallback HTML when GPT-5 unavailable"""
        return f"<html><body><h1>EQ12 - {prompt}</h1><p>GPT-5 fallback mode</p></body></html>"


# Global instance for EQ12 system
eq12_gpt5 = EQ12GPT5Integration()
