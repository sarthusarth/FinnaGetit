import json
from research_stage import research_stage


CURRENCY = "EUR" # Get from monetary account OR USD

def generate_dashboard(goal, duration, amount, monetary_account_id=2108197):
    """
    Runs the research_stage function and generates an HTML dashboard with the results.
    Args:
        goal: str, the goal of the user
        duration: int, the duration of the goal in months
        amount: float, the amount of money to save
        monetary_account_id: int, the id of the monetary account
    Returns:
        str: HTML content of the dashboard with populated values
    """
    # Run research_stage 
    print(f"Running research_stage for goal")
    print(f"Goal: {goal}")
    print(f"Duration: {duration}")
    print(f"Amount: {amount}")
    print(f"Monetary account id: {monetary_account_id}")
    result = research_stage(goal, duration, amount, monetary_account_id)

    print("Update HTML")
    
    # Extract required values from the result
    variable_expenses = result["variable_expenses"]

    slider_positions = result["slider_positions"]
    
    # Read the vanilla dashboard HTML template
    with open("./vanilla_savings_dashboard.html", "r") as file:
        html_content = file.read()
    
    # Replace initial values in JavaScript
    html_content = html_content.replace(
        "const goalAmount = 200;",
        f"const goalAmount = {amount};"
    )
    
    # Format variable expenses for JavaScript
    expenses_json = json.dumps(variable_expenses, indent=4)
    html_content = html_content.replace(
        "const initialExpenses = {\n            'restaurants': 65.91,\n            'groceries': 18.19,\n            'coffee': 13.27,\n            'shopping': 18.71,\n            'other': 7045.47\n        };",
        f"const initialExpenses = {expenses_json};"
    )
    
    # Set months limit
    html_content = html_content.replace(
        "const monthsLimit = 12;",
        f"const monthsLimit = {duration};"
    )
    
    # Set currency
    html_content = html_content.replace(
        "function formatCurrency(amount) {\n            return new Intl.NumberFormat('en-US', {\n                style: 'currency',\n                currency: 'USD',\n                minimumFractionDigits: 2\n            }).format(amount);\n        }",
        f"function formatCurrency(amount) {{\n            return new Intl.NumberFormat('en-US', {{\n                style: 'currency',\n                currency: '{CURRENCY}',\n                minimumFractionDigits: 2\n            }}).format(amount);\n        }}"
    )
    
    # Update $ signs in the HTML
    html_content = html_content.replace("$0", f"0 {CURRENCY}")
    
    # Update $ in chart labels and tooltips
    html_content = html_content.replace(
        "callback: value => '$' + value",
        f"callback: value => value + ' {CURRENCY}'"
    )
    
    # Modify script to initialize sliders with positions from research_stage
    modified_script = """
    // Initialize everything
    document.addEventListener('DOMContentLoaded', function() {
        createSliders();
        initializeChart();
        
        // Set slider positions from research_stage
        const sliderPositions = {
"""
    
    # Add slider positions as JavaScript object
    for category, value in slider_positions.items():
        modified_script += f"            '{category}': {value},\n"
    
    modified_script += """        };
        
        // Apply slider positions
        Object.keys(sliderPositions).forEach(category => {
            const slider = document.getElementById(`${category}-slider`);
            if (slider) {
                slider.value = sliderPositions[category];
                currentValues[category] = sliderPositions[category];
                
                // Update displays
                document.getElementById(`${category}-value`).textContent = formatCurrency(sliderPositions[category]);
                const savings = initialExpenses[category] - sliderPositions[category];
                document.getElementById(`${category}-savings`).textContent = `Monthly Savings: ${formatCurrency(savings)}`;
            }
        });
        
        // Update chart with initial values
        updateChart();
    });
    """
    
    # Replace the original initialization code
    html_content = html_content.replace(
        "        // Initialize everything\n        document.addEventListener('DOMContentLoaded', function() {\n            createSliders();\n            initializeChart();\n            updateChart();\n        });",
        modified_script
    )
    
    # Add plan description if needed
    if "plan_description" in result and result["plan_description"]:
        plan_description_html = """
    <div class="plan-description-container" style="margin-top: 24px; padding: 16px; background-color: #f8f9fa; border-radius: 8px;">
        <h2>Your Savings Plan</h2>
        <p>{0}</p>
    </div>
    """.format(result["plan_description"].replace('\n', '<br>'))
        html_content = html_content.replace("</body>", f"{plan_description_html}\n</body>")
    
    return html_content

def save_dashboard(goal, duration, amount, monetary_account_id):
    """
    Generates and saves the dashboard HTML to a file.
    """
    html_content = generate_dashboard(goal, duration, amount, monetary_account_id)
    with open("./dashboard_filled.html", "w") as file:
        file.write(html_content)
    print("Dashboard generated at './dashboard_filled.html'")

if __name__ == "__main__":
    save_dashboard(
        goal="Buy a new car",
        duration=12,
        amount=10000,
        monetary_account_id=2108197
    )
