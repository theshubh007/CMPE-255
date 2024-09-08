# Import necessary modules from FastAPI and other libraries
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Initialize the FastAPI app
app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient(config.MONGODB_URL)
db = client.expense_splitter


# Define a Pydantic model for the expense data
class Expense(BaseModel):
    user: str
    amount: float
    description: str


# Helper function to convert MongoDB documents to a JSON-serializable format
def expense_helper(expense) -> dict:
    return {
        "id": str(expense["_id"]),
        "user": expense["user"],
        "amount": expense["amount"],
        "description": expense["description"],
    }


# Endpoint to add a new expense
@app.post("/add_expense/")
async def add_expense(expense: Expense):
    await db.expenses.insert_one(expense.dict())
    return {"message": "Expense added successfully"}


# Endpoint to get all expenses
@app.get("/get_expenses/")
async def get_expenses():
    expenses = await db.expenses.find().to_list(1000)
    return [expense_helper(expense) for expense in expenses]


# Endpoint to split expenses among users
@app.get("/split_expenses/")
async def split_expenses():
    expenses = await db.expenses.find().to_list(1000)
    users = set(exp["user"] for exp in expenses)

    if not users:
        raise HTTPException(status_code=400, detail="No users to split expenses")

    total_amount = sum(exp["amount"] for exp in expenses)
    split_amount = total_amount / len(users)

    split_details = {user: split_amount for user in users}
    return split_details


# Serve static files (like HTML, CSS, JavaScript) from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Root endpoint to serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Open the index.html file and return its content as an HTML response
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Entry point of the application
if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app with Uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8000)
