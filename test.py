from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType



# Create an API context for production
api_context = ApiContext.create(
    ApiEnvironmentType.SANDBOX, # SANDBOX for testing
    "0af1027027c70fc025663392f8fc2b3d1427ac93b292eae3519672c0395fb814",
    "FinnaGetit"
)
# "Oaf1027027C70fc0256633928TC2b3d1427ac93b292eae3519672c0395fb814",

# Save the API context to a file for future use
api_context.save("bunq_api_context.conf")

# Load the API context into the SDK
BunqContext.load_api_context(api_context) 