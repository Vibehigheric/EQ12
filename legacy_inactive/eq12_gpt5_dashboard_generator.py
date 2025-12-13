#!/usr/bin/env python3
"""
EQ12 GPT-5 Enhanced Betting Dashboard Generator
Based on: https://github.com/openai/openai-cookbook/blob/main/examples/gpt-5/gpt-5_frontend.ipynb
"""

import base64

import openai


class EQ12GPT5DashboardGenerator:
    def __init__(self):
        self.client = openai.OpenAI()
        self.eq12_theme = "Dark theme with green accents, NHL branding, betting focus"

    def generate_betting_dashboard(
            self,
            dashboard_type: str,
            games_data: dict | None = None):
        """Generate betting dashboard using GPT-5 patterns"""

        prompts = {
            "tonight_games": f"Create an NHL betting dashboard for tonight's games showing {dashboard_type}. {
                self.eq12_theme}. Include live odds, parlay builders, and confidence indicators.",
            "analytics": f"Create a comprehensive NHL betting analytics dashboard with {dashboard_type}. {
                self.eq12_theme}. Include profit charts, win rate tracking, and model performance.",
            "mobile": f"Create a mobile-optimized NHL betting app interface for {dashboard_type}. {
                self.eq12_theme}. Touch-friendly, swipe navigation, quick bet placement.",
            "parlay_builder": f"Create an advanced parlay builder interface for {dashboard_type}. {
                self.eq12_theme}. Drag-and-drop bets, correlation warnings, profit calculators.",
        }

        prompt = prompts.get(dashboard_type, prompts["tonight_games"])

        if games_data:
            prompt += f" Include this data: {json.dumps(games_data)}"

        response = self.client.responses.create(model="gpt-5", input=prompt)

        return self.extract_html_from_response(response.output_text)

    def generate_multimodal_analysis(self, screenshot_path: str, analysis_request: str):
        """Analyze betting screenshots using GPT-5 multimodal capabilities"""

        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        input_data = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Analyze this betting screen: {analysis_request}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{encoded_image}",
                        "detail": "auto",
                    },
                ],
            }
        ]

        response = self.client.responses.create(model="gpt-5", input=input_data)

        return response.output_text

    def extract_html_from_response(self, text: str):
        """Extract HTML from GPT-5 response"""
        import re

        html_match = re.search(
            r"```html\s*(.*?)\s*```",
            text,
            re.DOTALL | re.IGNORECASE)
        return html_match.group(1) if html_match else text


# Integration with existing EQ12 system
gpt5_dashboard_generator = EQ12GPT5DashboardGenerator()
