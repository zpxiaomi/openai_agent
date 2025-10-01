from dotenv import load_dotenv
import os
import psycopg2
from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrail, function_tool
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
import asyncio

# Load .env file
load_dotenv()

class SupermarketOutput(BaseModel):
    is_supermarket_deal: bool
    reasoning: str


@function_tool
async def get_best_deal_data(category: str) -> str:
    """Fetch the best deal for a given category.

    Args:
        category: The category to fetch the best deal for.
    """
    print("get_best_deal_data called with category:", category)
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    print("DATABASE_URL:", db_url)
    # map category to sql query and fetch data from database
    category_name_to_id = {
        "meat": "fleischUndGefluegel",
        "snacks": "snacks",
        "vegetables": "Obst, Gemüse" 
    }
    category_id = category_name_to_id.get(category, None)
    print("category_id", category_id)
    if category_id is None:
        return f"Error: Invalid category '{category}'."
    sql_query = f"SELECT * FROM public.deals where category_level_1 = '{category_id}' order by discount_percentage desc limit 1;"
    print("SQL Query:", sql_query)

    try:
        with psycopg2.connect(db_url) as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(sql_query)
                records = cursor.fetchall()
                print(records)
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        return "Error: Unable to connect to the database. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Error: {e}"

    best_deals_fallback = {
        "meat": "Chicken breast at 5.99 EUR/kg",
        "snacks": "Chips at 1.49 EUR/bag",
        "dairy": "Milk at 0.89 EUR/liter"
    }

    if records is not None and len(records) > 0:
        return f"best deal for category '{category}' from datbase query are {records}."
    else:
        # no data found for category, use fallback
        return f"best deal for category '{category}' is {best_deals_fallback[category]}."


best_deal_in_category_agent = Agent(
    name="Best Deal expert",
    handoff_description="Spcialist agent for supermarket best deals",
    tools=[get_best_deal_data],
    instructions="You are an expert for best deals in the German supermarkets. You will provide help with the question about what is best deal for specific category." \
    " Give specific product recommendations and reason for recommending the product.",
)

supermarket_comparison_agent = Agent(
    name="Compare Supermarket deals",
    handoff_description="Specialist agent for deals in different supermarkets",
    instructions="You are a super market deals expert. You provide assistance with comparing deals in different supermarkets. Compare prices, quality, " \
    "and value across various supermarkets.", 
)

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about supermarket deals.",
    output_type=SupermarketOutput,
)

async def supermarket_deals_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(SupermarketOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_supermarket_deal,
    )

triage_agent = Agent( 
    name="Triage Agent",
    instructions="You are a triage agent. You determine which agent to use based on the user's supermarket related questions.",
    handoffs=[best_deal_in_category_agent, supermarket_comparison_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=supermarket_deals_guardrail)
    ]
)

async def main():
    # Example 1: supermarket deals question
    # what is the best deal for meat this week in the supermarkets?
    # what is the best deal for snacks this week in the supermarkets?
    # vegetables
    try:
        result = await Runner.run(triage_agent, "what is the best deal for vegetables this week in the supermarkets?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)
    # Example 2: compare supermarket with best deals question
    # try:
    #     result = await Runner.run(triage_agent, "Which super market has best deals for snacks this week in Germany?")
    #     print(result.final_output)
    # except InputGuardrailTripwireTriggered as e:
    #     print("Guardrail blocked this input:", e)   


if __name__ == "__main__":
    asyncio.run(main())
