import os
import socket

import uvicorn


def get_available_port(host: str, port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return port
        except OSError:
            for candidate in range(port + 1, port + 20):
                try:
                    sock.bind((host, candidate))
                    return candidate
                except OSError:
                    continue
            raise


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() in {"1", "true", "yes", "on"}
    port = get_available_port(host, port)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        workers=1,
    )


if __name__ == "__main__":
    main()
