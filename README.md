# Financial Goal Planner

A chatbot application that helps users plan and save for financial goals.

## Setup

### Environment Variables

Before running the application, you need to set up the Anthropic API key as an environment variable:

**For Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**For Windows (Command Prompt):**
```bash
set ANTHROPIC_API_KEY=your-api-key-here
```

**For Windows (PowerShell):**
```bash
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

### Permanent Setup

To avoid setting the environment variable each time you open a terminal:

**For Mac/Linux:**
Add to your `~/.bashrc`, `~/.zshrc`, or equivalent:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**For Windows:**
Set a permanent environment variable through the System Properties:
1. Search for "Environment Variables" in the Start menu
2. Click "Edit the system environment variables"
3. Click the "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `ANTHROPIC_API_KEY`
6. Variable value: your API key
7. Click "OK" to save

## Running the Application

After setting up the environment variable, you can run the application with:

```bash
python demo.py
```

# FinnaGetit

Agentic financial goal planner and data scientist for the Bunq app.

Example workflow: 

Step 1: Goal definition
    user prompt: I am going to Vietnam, backpacking in 6 months.
    system: following-up, for how long are you going? do you have a budget you need in mind?
    user: i'll go for 1 month, I travel light
    system: using search I've found that you'll need about 1.2k (excluding tickets). Goal defined: 1.2k additional savings in 6 months

    Options: Accept |  Change_Quantity  | Change_duration

    user: Accept



### API connection 

