FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        iperf3 \
        iproute2 \
        openssh-client \
        procps \
        sshpass \
        sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/hpe/winlab_e2e_rapp

COPY requirements-container.txt /tmp/requirements-container.txt
RUN pip install --no-cache-dir -r /tmp/requirements-container.txt

CMD ["bash", "-lc", "python -m uvicorn winlab_e2e_rapp.app:app --host ${WINLAB_E2E_BIND_HOST:-127.0.0.1} --port ${WINLAB_E2E_BIND_PORT:-19090}"]
