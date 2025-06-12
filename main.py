# External imports
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

# Local import for the Torre service function
from services.torre_services import perform_torre_people_search


app = FastAPI(
    title="Torre AI Challenge API",
    description="Backend API for searching people on Torre.ai",
    version="0.0.1",
)

TORRE_SEARCH_URL = "https://torre.ai/api/entities/_searchStream"


@app.get("/")
async def read_root():
    """
    A root endpoint to confirm the API is running.
    """
    return {"message": "Root working"}


@app.get("/search-people")  # Changed path for clarity
async def search_people(
    query: str = Query(
        ..., min_length=2, description="The name or keyword to search in Torre."
    )
):
    """
    Searches for people on Torre.ai based on a given query.
    Returns a list of matching person profiles.
    """
    if not query.strip():  # Basic validation
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Call our simplified search function directly
        people_results = await perform_torre_people_search(query)

        if not people_results:
            # Return an empty list and a message if no results
            return JSONResponse(
                status_code=200, content={"message": "No people found.", "results": []}
            )

        # Return the results directly
        return people_results
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve search results due to an internal error.",
        )


# -- Run the application --
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
