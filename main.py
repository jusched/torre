# External modules
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Local modules
from services.torre_services import perform_torre_people_search, get_person_profile

app = FastAPI(
    title="Torre AI Challenge API",
    description="Backend API for searching people on Torre.ai",
    version="0.0.1",
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null",  # Allows requests from file:/// for local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://torre-front.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# * --- FastAPI Endpoints ---
@app.get("/")
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Torre AI Test working!"}


@app.get("/search-people")
async def search_people(
    query: str = Query(
        ..., min_length=2, description="The name or keyword to search for people."
    )
):
    """
    Searches for people on Torre.ai based on a given query.
    Returns a list of matching person profiles.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Call the service function to perform the search
        people_results = await perform_torre_people_search(query)

        if not people_results:
            return JSONResponse(
                status_code=200, content={"message": "No people found.", "results": []}
            )

        return people_results
    except HTTPException:
        # Re-raise HTTPExceptions from the service layer directly
        raise
    except Exception as e:
        print(f"An unexpected error occurred in search_people endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve search results due to an internal error.",
        )


@app.get("/profile/{username}")
async def get_person_profile_endpoint(
    username: str,
):
    """
    Retrieves the genome information for a given username from Torre.ai.
    """
    try:
        # Call the service function to get the profile
        profile_data = await get_person_profile(username)
        return profile_data
    except HTTPException:
        # Raise HTTPExceptions from the service layer directly
        raise
    except Exception as e:
        print(f"An unexpected error occurred in get_person_profile_endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve profile details due to an internal error.",
        )


# --- Run the application ---
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
