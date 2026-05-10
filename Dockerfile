FROM python:3.13-slim

WORKDIR /app

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip gcc python3-dev git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deno.land/install.sh | sh

ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock ./

# Try uv sync first, fall back to pip if uv fails
RUN uv sync --frozen 2>/dev/null || pip install --no-cache-dir -r <(uv pip compile pyproject.toml) 2>/dev/null || pip install --no-cache-dir -e .

COPY . .

CMD ["bash", "start"]
