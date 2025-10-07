import os
import base64
from openai import OpenAI
from .schemas import MealAnalysis

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_meal_image(image_data: bytes) -> dict:
    """
    Analyze meal image using OpenAI and return structured nutritional data
    """
    try:
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "You are a professional nutritionist and food analysis expert. Analyze meal images and provide detailed nutritional information for each food item detected. Be accurate and thorough in your analysis."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """Analyze this meal photo in detail. For each food item you can identify:
1. Identify the food name clearly
2. Estimate the portion size (e.g., '1 burger (250g)', 'medium serving (150g)')
3. Provide complete nutritional information including:
   - Macronutrients (calories, carbs, fat, protein)
   - Minerals (calcium, iron, magnesium, potassium, zinc)
   - Vitamins (A, B9, B12, C, D)
   - Additional nutrients (cholesterol, fiber, omega-3, saturated fat, sodium)

Use appropriate units: kcal for calories, g for macros and some nutrients, mg for most minerals and some vitamins, mcg for other vitamins.
Be specific and accurate with measurements."""
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ],
            text_format=MealAnalysis,
        )
        
        parsed_data = response.output_parsed
        return parsed_data.model_dump()
        
    except Exception as e:
        print(f"Error analyzing image with OpenAI: {str(e)}")
        raise