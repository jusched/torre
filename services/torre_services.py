import httpx, json

TORRE_SEARCH_URL = "https://torre.ai/api/entities/_searchStream"


async def torre_people_search(query: str) -> list:
    """
    Makes a POST request to Torre AI _searchStream endpoint and
    collects all results into a list.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"query": query, "identityType": "person"}

    results = []
    buffer = b""
    # Async POST request to Torre AI's search endpoint
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                TORRE_SEARCH_URL,
                headers=headers,
                json=payload,
                timeout=30.0,
            ) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    buffer += chunk  # Add the new chunk to the buffer

                    # Split the buffer by newline.
                    # rsplit(b'\n', 1) is key: it splits only once from the right
                    # to keep the last (potentially incomplete) line in the buffer.
                    # The rest are full lines.
                    lines = buffer.split(b"\n")

                    # The last element in 'lines' might be an incomplete line
                    # if the chunk didn't end with a newline.
                    # Keep it in the buffer for the next chunk.
                    buffer = lines.pop() if lines[-1:] else b""

                    for line_bytes in lines:
                        # Decode the full line bytes to string before parsing JSON
                        line_str = line_bytes.decode(
                            "utf-8", errors="ignore"
                        ).strip()  # Use errors='ignore' for robustness against malformed bytes, or 'replace'
                        if line_str:
                            try:
                                data = json.loads(line_str)
                                results.append(data)
                            except json.JSONDecodeError as e:
                                print(
                                    f"JSON decoding error in stream: {e} in line: {line_str}"
                                )
                                # It's okay to continue if one line is malformed,
                                # but the buffer logic should prevent most issues.
                                continue
        except httpx.RequestError as exc:
            print(f"Network or request error: {exc}")
            raise httpx.RequestError(
                status_code=503, detail="Could not connect to Torre AI service."
            )
        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error response from Torre AI: {exc.response.status_code} - {exc.response.text}"
            )
            raise httpx.RequestError(
                status_code=exc.response.status_code,
                detail=f"Error from Torre AI: {exc.response.text}",
            )
        except Exception as e:
            print(f"An unexpected error occurred in perform_torre_people_search: {e}")
            raise  # Re-raise for the main endpoint to catch

    return results
