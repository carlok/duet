# Isolated environment for the two-operation theory search. Free software only, versions pinned.
# z3 effort numbers depend on the z3 version: keep z3-solver pinned, never compare across versions.
# 5.4.1.0 has an aarch64 wheel, so the Mac and the cloud sessions use the same z3.
FROM docker.io/library/python:3.13.18-slim
RUN pip install --no-cache-dir numpy==2.5.3 numba==0.68.1 z3-solver==5.4.1.0 pytest==9.0.1
# Data (matrix, corpus, queue, results, journal, logs) lives in the mounted volume, never in the image.
ENV SOUP_DATA=/data \
    NUMBA_CACHE_DIR=/data/.cache/numba \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY soup /app/soup
COPY tests /app/tests
COPY results-cloud /app/results-cloud
COPY run.sh pytest.ini /app/
CMD ["bash", "run.sh"]
