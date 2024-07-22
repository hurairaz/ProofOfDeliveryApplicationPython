from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
import jwt
import schemas

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            try:
                payload = decode_jwt_token(credentials.credentials)
                # Token is valid, you can use payload if needed
                return payload.get("email")
            except HTTPException as e:
                raise e  # Re-raise the exception from decode_jwt_token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


def create_jwt_token(data: dict):
    payload = data.copy()
    access_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": access_token_expires})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "jwt_token": token
    }


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload = {'email': 'username@gmail.com', 'exp': 1721675711}
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# def main():
#     # Sample data to encode
#     data = {"email": "username@gmail.com"}
#
#     # Create access token
#     token_response = create_jwt_token(data)
#     print(f"Encoded Token: {token_response.access_token}")
#
#     # Decode the token
#     try:
#         decoded_data = decode_jwt_token(token_response.access_token)
#         print(f"Decoded Data: {decoded_data}")
#     except HTTPException as e:
#         print(f"Error: {e.detail}")
#
#
# if __name__ == "__main__":
#     main()