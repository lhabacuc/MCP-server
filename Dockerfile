FROM python:3.3.11-bookworm

LABEL maintainer="MCP DevOps Agent"
LABEL version="1.0.0"

RUN apt-get update && apt-get install -y \
    gcc \
    make \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pyinstaller

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

EXPOSE 8080

CMD ["python", "web_server.py"]

FROM python:3.3.11-bookworm as builder

WORKDIR /build

RUN apt-get update && apt-get install -y \
    gcc \
    make \
    binutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pyinstaller

COPY . .

RUN pyinstaller --name mcp-agent \
    --onefile \
    --add-data "index.html:." \
    --add-data "mcp_pc_devops_agent.py:." \
    --hidden-import=mcp \
    --hidden-import=fastmcp \
    --hidden-import=groq \
    --hidden-import=aiohttp \
    --collect-all mcp \
    web_server.py

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=builder /build/dist/mcp-agent /app/mcp-agent
COPY index.html /app/
COPY mcp_pc_devops_agent.py /app/

ENV DISPLAY=:0

EXPOSE 8080

CMD ["/app/mcp-agent"]
