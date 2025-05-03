""" Implement research stage

func(goal: str, duration: time, amount: float) -> dict:


{
fixed_expenses: {category_1: float, category_2: float, category_3: float}, , 
variable_expenses: {category_1: float, category_2: float, category_3: float}, 
scheduled_expenses: {category_1: float, category_2: float, category_3: float}, 

"""

from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import PaymentApiObject
from bunq import Pagination

from openai import OpenAI
import json
from config import NVIDIA_KEY

api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)

import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
#model = "claude-3-7-sonnet-20250219"
model = "claude-3-5-sonnet-20240620"
"""
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = NVIDIA_KEY
)"""

def get_scheduled_payments(monetary_account_id: int) -> int:
    return 200

def get_fixed_payments(monetary_account_id: int) -> int:
    """Return integer because fixed expenses cannot really be reduced """
    return 1000

def get_variable_payments(monetary_account_id: int) -> dict:
    """Return categorized variable payments with sums by category"""
    # Get all payments for the monetary account
    pagination = Pagination()
    pagination.count = 200  # Get more transactions at once

    # List payments for the specified monetary account
    payments = PaymentApiObject.list(
        monetary_account_id=monetary_account_id,
        params=pagination.url_params_count_only
    ).value

    # Collect payment information for processing
    breakdown = []
    for payment in payments:
        payment_amount = float(payment.amount.value)
        if payment_amount > 0:
            # this is not an expense, ignore
            continue
        else:
            payment_amount = abs(payment_amount)

            breakdown.append({
                "id": payment.id_, 
                "name": payment.description, 
                "value": payment_amount
            })
    
    # Skip processing if no payments found
    if not breakdown:
        return {
            "restaurants": 0,
            "groceries": 0,
            "coffee": 0,
            "shopping": 0,
            "other": 0
        }
    
    # Prepare prompt for LLM categorization
    prompt = """
    Categorize each of the following transactions into one of these categories: restaurants, groceries, coffee, shopping, other.
    Then sum the total amount for each category.
    
    Transactions:
    {}
    
    IMPORTANT: Return ONLY a valid JSON object with categories as keys and total amounts as values. No explanations or other text.
    """.format(str(breakdown))
    
    # Process with Llama 3.3 70B model
    print("PROMPT", prompt)
    completion = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.01,
        top_p=0.95,
        max_tokens=1024
    )
    print("COMPLETION", completion)
    # Extract categorized results
    try:
        import json
        response_text = completion.content[0].text
        
        # Try to extract JSON if there's other text
        if "```json" in response_text:
            # Extract content between ```json and ```
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Clean any remaining non-JSON text
        response_text = response_text.strip()
        #if response_text.startswith('```') and response_text.endswith('```'):
        #    response_text = response_text[3:-3].strip()
            
        result = json.loads(response_text)
        return result
    except Exception as e:
        # Fallback if parsing fails
        print("PARSING FAILED", completion.content[0].text, "ERROR", e)
        return {
            "restaurants": 0,
            "groceries": 0,
            "coffee": 0, 
            "shopping": 0,
            "other": 0
        }



def research_stage(goal: str, duration: int, amount: float, monetary_account_id: int) -> dict:
    """
    Implement research stage.
    
    Args: 
        goal: str, 
        duration: int, in months
        amount: float
        monetary_account_id: int, the ID of the monetary account to analyze
    Returns:
        dict: A dictionary with the following keys:
            - "fixed_expenses": float, the fixed expenses
            - "variable_expenses": float, the variable expenses
            - "scheduled_expenses": float, the scheduled expenses
            - "slider_positions": dict, the slider positions
            - "percent_decrease_per_category": dict, the percentage decrease per category
            - "plan_description": str, the plan description
    """

    # Get all payments for the monetary account
    pagination = Pagination()
    pagination.count = 200  # Get more transactions at once

    # List payments for the specified monetary account
    payments = PaymentApiObject.list(
        monetary_account_id=monetary_account_id,
        params=pagination.url_params_count_only
    ).value

    print("MAKING BUNQ API CALLS AND LLM ANALYSIS")
    fixed_payments = get_fixed_payments(monetary_account_id)
    variable_payments = get_variable_payments(monetary_account_id)
    scheduled_payments = get_scheduled_payments(monetary_account_id)

    print("GETTING SLIDER POSITIONS")
    # Get the slider positions ie, savings per category
    slider_positions, percent_decrease_per_category = get_slider_positions(duration, amount,variable_payments,  monetary_account_id)

    print("GENERATING PLAN DESCRIPTION")
    # Now we have all the information, generate the full text
    full_info_for_result = f"""
    You are a personal datascientist agent for the Bunq app. You help users realise their dreams by getting them closer to their
    financial goals.

    This user wants to save {amount} in {duration} months. That's around {amount / duration} per month.

    On a monthly basis the user has the following expenses:
    - Fixed expenses: {fixed_payments}
    - Variable expenses: {variable_payments}
    - Scheduled payments: {scheduled_payments}

    Your proposed solution is to reduce the variable expenses by the following percentages:
    {percent_decrease_per_category}
    and in absolute terms:
    {slider_positions}

    Using all the information above the user will see a dashboard with their simulated savings accumulation. Your job is to accompany this dashboard
    by justifying the various saving choices outlined above. If possible provide tips on the Fixed and Scheduled payments for additional savings.
    Explain to the user that the simulation includes some random variations based on their previous spending behaviours during similar months, to better reflect real-world spending patterns.

    Explain all this to the user very concisely but in a playfull and engaging way. Don't be too verbose. Remind the user that no one is perfect so they don't have to be and that
    you will be together to help them get to their goal. Depending on their goal end on something motivating. For example if the goal is to save for a backpacking trip to
    Vietnam you could end with: "Don't worry, together we will get you there!"
    """

    # Generate the plan description
    plan_description = get_plan_description(full_info_for_result)
    # print("PROMPT", full_info_for_result)
    return {
        "fixed_expenses": fixed_payments,
        "variable_expenses": variable_payments,
        "scheduled_expenses": scheduled_payments,
        "slider_positions": slider_positions,
        "percent_decrease_per_category": percent_decrease_per_category,
        "plan_description": plan_description
    }


def get_slider_positions(duration: int, amount: float, variable_payments: dict, monetary_account_id: int) -> dict:
    """
    Set initial slider positions for each expense category using LLM recommendations.
    
    Args:
        duration: int, in how many months the user wants to save the money
        amount: float, the amount of money to save
        monetary_account_id: int, the ID of the monetary account to analyze
        
    Returns:
        dict: Initial slider positions for each expense category and the percentage decrease per category that this selection represents
    """
    
    # If there are no expenses, return default positions
    if not variable_payments or all(value == 0 for value in variable_payments.values()):
        return {
            "restaurants": 0,
            "groceries": 0,
            "coffee": 0,
            "shopping": 0,
            "other": 0
        }
    
    # Prepare prompt for LLM to suggest reduction percentages
    expense_data = "\n".join([f"{category}: ${amount:.2f}" for category, amount in variable_payments.items()])
    
    prompt = f"""
    Based on the following monthly expense data:
    {expense_data}

    The user wants to save {amount} in {duration} months. That's around {amount / duration} per month.
    
    Suggest reasonable reduction percentages (0-70%) for each category to help save money:
    - For essential categories like groceries, suggest lower reduction percentages
    - For luxury/optional categories like restaurants or coffee, suggest higher reduction percentages
    - For shopping and other categories, suggest moderate reduction percentages based on their amounts
    - Make sure that the savings get the user as closely as possible to the goal based on the required savings (estimated by goal / months)
    
    IMPORTANT: Return ONLY a valid JSON object with categories as keys and reduction percentages (0-120) as values per category.
    """
    
    # Process with LLM
    completion = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.01,
        top_p=0.95,
        max_tokens=1024
    )
    print("COMPLETION", completion)
    response_text = completion.content[0].text
    print("RESPONSE TEXT", response_text)
    json_match = json.loads(response_text)
    print("JSON MATCH", json_match)

    # Extract recommended reduction percentages
    slider_positions = {}
    percent_decrease_per_category = {}
    for category, percentage in json_match.items():
        if category in variable_payments:
            # Ensure percentage is between 0-100
            percentage = max(0, min(100, float(percentage)))
                # Calculate slider position based on percentage, get absolute value of the amount
            slider_positions[category] = abs(variable_payments[category] - variable_payments[category] * percentage / 100)
            percent_decrease_per_category[category] = percentage
        # Ensure all categories from variable_expenses are included
    for category in variable_payments:
            if category not in slider_positions:
                slider_positions[category] = 0
                
    return slider_positions, percent_decrease_per_category
    



def get_plan_description(full_info_for_result: str) -> str:
    """
    Generate a user-friendly plan description using LLM based on the provided information.
    
    Args:
        full_info_for_result: str, the prompt with all savings information
        
    Returns:
        str: Generated plan description
    """
    # Process with LLM to generate plan description
    completion = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": full_info_for_result}],
        temperature=0.7,
        top_p=0.9,
        max_tokens=800
    )
    
    # Extract generated description - using OpenAI client structure here
    return completion.content[0].text.strip()




if __name__ == "__main__":
    print(research_stage("Buy a new car", 6, 1000, 2108197))
