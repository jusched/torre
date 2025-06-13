import httpx
import json
from fastapi import HTTPException

# Torre AI API URLs
TORRE_SEARCH_STREAM_URL = "https://torre.ai/api/entities/_searchStream"
TORRE_GENOME_BIO_BASE_URL = "https://torre.ai/api/genome/bios"


async def perform_torre_people_search(query: str) -> list:
    """
    Makes a POST request to Torre AI _searchStream endpoint and
    collects all results into a list, correctly handling partial lines in stream.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"query": query, "identityType": "person"}

    results = []

    # Initialize a buffer to hold incomplete lines and avoid decode errors
    # This is necessary to handle cases where the stream may split a JSON object across chunks
    buffer = b""

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                TORRE_SEARCH_STREAM_URL,
                headers=headers,
                json=payload,
                timeout=30.0,
            ) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors

                # aiter_bytes() allows us to read the response in chunks
                async for chunk in response.aiter_bytes():

                    # Append the new chunk to the buffer
                    buffer += chunk

                    # Split the buffer into lines
                    # This will handle cases where the last line may not end with a newline
                    lines = buffer.split(b"\n")

                    # Keep any incomplete line in the buffer for the next chunk
                    buffer = (
                        # If the last line is incomplete, keep it in the buffer, else reset the buffer
                        lines.pop()
                        if lines and not lines[-1].endswith(b"\n")
                        else b""
                    )

                    for line_bytes in lines:

                        # Decode each line, ignoring errors to handle malformed UTF-8
                        line_str = line_bytes.decode("utf-8", errors="ignore").strip()
                        if line_str:
                            try:
                                data = json.loads(line_str)
                                results.append(data)
                            except json.JSONDecodeError as e:
                                print(
                                    f"JSON decoding error in stream: {e} in line: '{line_str}'"
                                )
                                continue  # Skip this malformed line and continue processing

        except httpx.RequestError as exc:
            print(f"Network or request error: {exc}")
            raise HTTPException(
                status_code=503, detail="Could not connect to Torre AI search service."
            )
        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error response from Torre AI search: {exc.response.status_code} - {exc.response.text}"
            )
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from Torre AI search: {exc.response.text}",
            )
        except Exception as e:
            print(f"An unexpected error occurred in perform_torre_people_search: {e}")
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred during search."
            )

    return results


async def get_person_profile(username: str) -> dict:
    """
    Retrieves the genome information for a given username from Torre.AI.
    Trigger when clicking "View Details" on the frontend.
    """
    TORRE_GENOME_BIO_URL = f"{TORRE_GENOME_BIO_BASE_URL}/{username}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(TORRE_GENOME_BIO_URL, timeout=10.0)
            response.raise_for_status()  # This handles error HTTP status codes returned by Torre AI

            profile_data = response.json()

            # Check for 'errors' array in the response JSON even if HTTP status is 200 OK
            if (
                "errors" in profile_data
                and isinstance(profile_data["errors"], list)
                and profile_data["errors"]
            ):
                error_info = profile_data["errors"][0]
                error_code = error_info.get("code", "N/A")
                error_message = error_info.get(
                    "message", "Unknown error from Torre AI Genome API"
                )

                # '020000' is a common code for 'resource not found' or 'invalid identifier' from Torre
                if error_code == "020000":
                    raise HTTPException(
                        status_code=404,
                        detail=f"Profile '{username}' not found on Torre.ai or invalid identifier.",
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Torre AI Genome API error ({error_code}): {error_message}",
                    )

            # If no errors array, return the parsed profile data
            return profile_data

        except httpx.RequestError as exc:
            print(f"Network or request error fetching genome for {username}: {exc}")
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to Torre AI Genome service for {username}.",
            )

        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error response from Torre AI Genome for {username}: {exc.response.status_code} - {exc.response.text}"
            )
            if exc.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Profile for '{username}' not found on Torre.ai.",
                )
            else:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Error from Torre AI: {exc.response.text}",
                )

        except Exception as e:
            print(
                f"An unexpected error occurred while fetching profile for {username}: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve profile details due to an internal error.",
            )
