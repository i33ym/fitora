import os, io, base64
from openai import OpenAI
from .schemas import MealAnalysis

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_meal_image(image_data: bytes, language: str = 'en') -> dict:
    """
    Analyze meal image using OpenAI and return structured nutritional data
    """
    try:
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        language_prompts = {
            'en': 'Analyze this image in English.',
            'uz': 'Rasmni tahlil qiling va o\'zbekcha javob bering.',
            'uz-cyrl': 'Расмни таҳлил қилинг ва ўзбекча жавоб беринг.',
            'ru': 'Проанализируйте это изображение и ответьте на русском языке.'
        }
        
        prompt = language_prompts.get(language, language_prompts['en'])
        
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "You are a professional nutritionist and food analysis expert. Your job is to determine if an image contains food, and if so, analyze it for nutritional information."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"""{prompt}

CRITICAL: First, determine if this image contains actual food or beverages.
- If the image shows food or drinks, set is_food to true and analyze it.
- If the image shows people, animals, objects, scenery, or anything else that is NOT food, set is_food to false, confidence to 'high', and return an empty foods array.

If it IS food, for each food item you can identify:
1. Identify the food name clearly
2. Estimate the portion size (e.g., '1 burger (250g)', 'medium serving (150g)')
3. Set confidence level (high/medium/low) based on image clarity
4. Provide complete nutritional information including:
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

def analyze_meal_voice(audio_data: bytes, language: str = 'uz') -> dict:
    try:
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"
        
        whisper_language = None
        if language == 'ru':
            whisper_language = 'ru'
        elif language == 'en':
            whisper_language = 'en'
        
        if whisper_language:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                language=whisper_language
            )
        else:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file
            )
        
        transcribed_text = transcription.text

        language_prompts = {
            'en': 'in English',
            'uz': 'o\'zbekcha',
            'uz-cyrl': 'ўзбекча',
            'ru': 'на русском языке'
        }
        
        lang_instruction = language_prompts.get(language, language_prompts['uz'])
        
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": f"You are a professional nutritionist. Based on meal descriptions, estimate nutritional content. Respond {lang_instruction}."
                },
                {
                    "role": "user",
                    "content": f"""Based on this meal description, estimate the nutritional content: "{transcribed_text}"

For each food item mentioned:
1. Identify the food name
2. Estimate portion size (make reasonable assumptions if not specified)
3. Provide nutritional information:
   - Macronutrients (calories, carbs, fat, protein)
   - Minerals (calcium, iron, magnesium, potassium, zinc)
   - Vitamins (A, B9, B12, C, D)
   - Additional nutrients (cholesterol, fiber, omega-3, saturated fat, sodium)

Use appropriate units: kcal for calories, g for macros, mg for minerals, mcg for vitamins.
If portions aren't specified, use standard serving sizes."""
                }
            ],
            text_format=MealAnalysis,
        )
        
        parsed_data = response.output_parsed
        result = parsed_data.model_dump()
        result['transcription'] = transcribed_text
        
        return result
        
    except Exception as e:
        print(f"Error analyzing voice with OpenAI: {str(e)}")
        raise