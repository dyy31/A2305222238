# logger_middleware.py
import requests

LOG_URL = "http://20.244.56.144/evaluation-service/logs"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJkaXZ5YW5zaC55YWRhdkBzLmFtaXR5LmVkdSIsImV4cCI6MTc1NDM3MzgzOSwiaWF0IjoxNzU0MzcyOTM5LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNzc3MmFmNTMtZjkyZi00MDA3LWJkNTMtZjVhODM4ZGMyOGFjIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoiZGl2eWFuc2ggeWFkYXYiLCJzdWIiOiJlYmJmMmRiYS1lZmYzLTQ1NGQtOGE2Zi03YzAwNjRhNGMzZGYifSwiZW1haWwiOiJkaXZ5YW5zaC55YWRhdkBzLmFtaXR5LmVkdSIsIm5hbWUiOiJkaXZ5YW5zaCB5YWRhdiIsInJvbGxObyI6ImEyMzA1MjIyMjM4IiwiYWNjZXNzQ29kZSI6Inl2aGRkYSIsImNsaWVudElEIjoiZWJiZjJkYmEtZWZmMy00NTRkLThhNmYtN2MwMDY0YTRjM2RmIiwiY2xpZW50U2VjcmV0Ijoia3p1cGRZSndaV1d5dnh6diJ9.mn_J2IxV1Dx3pAz6_H8X-ehgiT1B0Fl1hn4jcvHq1IQ"

def log(stack: str, level: str, pkg: str, message: str):
   
    try:
        res = requests.post(
            LOG_URL,
            json={"stack": stack, "level": level, "package": pkg, "message": message},
            headers={"Authorization": f"Bearer {TOKEN}"}
        )

        
        res.raise_for_status()
    except Exception as e:
        print(f"Logging failed: {e}")

async def logging_middleware(request, call_next):
   


    log("backend", "info", "request", f"{request.method} {request.url}")
    response = await call_next(request)
    log("backend", "info", "response", f"Status {response.status_code}")
    return response
