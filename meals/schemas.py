from pydantic import BaseModel, Field
from typing import List

class Nutritions(BaseModel):
    calories: str = Field(description="Calories with unit (e.g., '780 kcal')")
    carbs: str = Field(description="Carbohydrates with unit (e.g., '45 g')")
    fat: str = Field(description="Fat with unit (e.g., '45 g')")
    protein: str = Field(description="Protein with unit (e.g., '40 g')")
    fiber: str = Field(description="Fiber with unit (e.g., '3 g')")

class Minerals(BaseModel):
    calcium: str = Field(description="Calcium with unit (e.g., '200 mg')")
    iron: str = Field(description="Iron with unit (e.g., '5 mg')")
    magnesium: str = Field(description="Magnesium with unit (e.g., '50 mg')")
    potassium: str = Field(description="Potassium with unit (e.g., '400 mg')")
    zinc: str = Field(description="Zinc with unit (e.g., '5 mg')")
    sodium: str = Field(description="Sodium with unit (e.g., '1200 mg')")
    selenium: str = Field(description="Selenium with unit (e.g., '10 mg')")

class Vitamins(BaseModel):
    vitamin_a: str = Field(description="Vitamin A with unit (e.g., '150 mcg')")
    vitamin_b12: str = Field(description="Vitamin B12 with unit (e.g., '3 mcg')")
    vitamin_b9: str = Field(description="Vitamin B9 (Folate) with unit (e.g., '50 mcg')")
    vitamin_c: str = Field(description="Vitamin C with unit (e.g., '5 mg')")
    vitamin_d: str = Field(description="Vitamin D with unit (e.g., '0.5 mcg')")
    vitamin_e: str = Field(description="Vitamin E with unit (e.g., '0.5 mcg')")
    vitamin_k: str = Field(description="Vitamin K with unit (e.g., '0.5 mcg')")
    vitamin_b6: str = Field(description="Vitamin B6 with unit (e.g., '0.5 mcg')")

class Fats(BaseModel):
    cholesterol: str = Field(description="Cholesterol with unit (e.g., '120 mg')")
    omega_3: str = Field(description="Omega-3 with unit (e.g., '0.2 g')")
    saturated_fat: str = Field(description="Saturated fat with unit (e.g., '18 g')")
    unsaturated_fat: str = Field(description="Unsaturated fat with unit (e.g., '18 g')")
    omega_6: str = Field(description="Omega-6 with unit (e.g., '0.2 g')")

class Food(BaseModel):
    name: str = Field(description="Name of the food or drink item")
    portion_size: str = Field(description="Estimated portion size (e.g., '1 burger (250g)', 'medium serving')")
    nutritions: Nutritions = Field(description="Macronutrients information")
    minerals: Minerals = Field(description="Mineral content")
    vitamins: Vitamins = Field(description="Vitamin content")
    fats: Fats = Field(description="Fats content")

class MealAnalysis(BaseModel):
    foods: List[Food] = Field(description="List of all identified food items in the image")