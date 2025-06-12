import httpx, json

TORRE_SEARCH_URL = "https://torre.ai/api/entities/_searchStream"


async def perform_torre_people_search(query: str) -> list:
    """
    Makes a POST request to Torre AI _searchStream endpoint and
    collects all results into a list.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"query": query, "identityType": "person"}

    results = []
    # Async POST request to Torre AI's search endpoint
    async with httpx.AsyncClient() as client:
        try:
            # Send the POST request. Read line by line
            async with client.stream(
                "POST",
                TORRE_SEARCH_URL,
                headers=headers,
                json=payload,
                timeout=30.0,
            ) as response:
                response.raise_for_status()  # Check for HTTP errors

                # Process the response stream line by line
                async for chunk in response.aiter_bytes():
                    for line in chunk.decode("utf-8").splitlines():
                        line = line.strip()
                        if line:  # Make sure the line isn't empty
                            try:
                                data = json.loads(line)
                                # Add parsed data to results
                                results.append(data)
                            except json.JSONDecodeError as e:
                                print(
                                    f"JSON decoding error in stream: {e} in line: {line}"
                                )
                                continue

        except httpx.RequestError as exc:
            print(f"Network or request error: {exc}")
            raise
        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error response: {exc.response.status_code} - {exc.response.text}"
            )
            raise

    return results
