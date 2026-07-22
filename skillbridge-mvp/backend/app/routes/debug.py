from fastapi import APIRouter, HTTPException, Request, status

from app.utils.jwt_handler import verify_token

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/headers")
def echo_headers(request: Request):
    # Return the raw Authorization header and a small set of headers for debugging
    auth = request.headers.get("authorization")
    return {
        "authorization": auth,
        "host": request.headers.get("host"),
        "origin": request.headers.get("origin"),
        "user_agent": request.headers.get("user-agent"),
    }


@router.get("/verify")
def verify_auth(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Authorization header")

    # Support both 'Bearer <token>' and raw token
    token = auth.split(" ", 1)[1] if " " in auth else auth
    payload = verify_token(token)
    return {"payload": payload}
