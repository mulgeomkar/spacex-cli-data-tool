
# SpaceX CLI Data Tool

## Problem statement

Fetch data from a public API you choose, persist it locally, and expose simple CLI queries.


## Solution
![SpaceX Logo](Image.png)


## API Chosen

- **SpaceX API v4**  
  Public, free API for real launch data  
  [Docs & Source](https://github.com/r-spacex/SpaceX-API)

***

## Setup

```bash
pip install -r requirements.txt
```
- Requires Python 3.7+
- No authentication needed

***

## Rate-limit Handling

- Automatically detects HTTP 429 (Too Many Requests)
- Waits for `Retry-After` header, then exponentially backs off for up to 5 attempts
- Ensures robust ingestion even when API is overloaded

***

## Table Schema

| Field         | Type      | Description                   |
|---------------|-----------|-------------------------------|
| id            | TEXT      | SpaceX launch ID (unique)     |
| flight_number | INTEGER   | Launch sequence number        |
| name          | TEXT      | Mission name                  |
| date_utc      | TEXT      | UTC scheduled date/time       |
| success       | BOOLEAN   | Mission success (True/False)  |
| details       | TEXT      | Mission description/details   |
| rocket        | TEXT      | Rocket name                   |
| launchpad     | TEXT      | Launchpad name                |

**Indexes:**  
- `success`, `rocket`, and `date_utc` for fast queries and filters

**Rationale:**  
Schema covers all key attributes to query historical launches, analyze outcomes, or filter by rocket/launchpads. Index fields are chosen for speed and typical analysis!

***

## Example Commands

- Fetch launches and cache data:
    ```
    python api_tool.py fetch --param 50
    ```
- Query launches for successes:
    ```
    python api_tool.py query --filter "success:true" --limit 5
    ```
- Query for a specific rocket:
    ```
    python api_tool.py query --filter "rocket:Falcon 9" --limit 3
    ```
- Combine filters:
    ```
    python api_tool.py query --filter "rocket:Falcon 9,success:true" --limit 5
    ```

***

## Known Limitations

- Only supports simple key:value filters (no ranges, LIKE, or regex)
- Boolean values require `true`/`false` (no 1/0)
- Filters must match exact DB column names
- Query result limited by SQLite capabilities, not joined with external tables
- CLI only, no web interface or visualization included
- Rate limits may still block heavy usage beyond 5-retry backoff

## Demo video
[![Watch the demo](https://img.youtube.com/vi/qxgsJ055SuQ/0.jpg)](https://www.youtube.com/watch?v=qxgsJ055SuQ)



