# Isolated environment for the two-operation theory search. Free software only, versions pinned.
# z3 effort numbers depend on the z3 version: keep z3-solver pinned, never compare across versions.
# 5.4.1.0 has an aarch64 wheel, so the Mac and the cloud sessions use the same z3.
# ---- E prover, built from pinned source (Ubuntu's 3.0.03 package is a crashing debug build)
FROM docker.io/library/python:3.13.18-slim AS eprover
ARG E_VERSION=3.2.5
ARG E_SHA256=de98e5d972318c08cf8ff5f14f8a0a911715200de828637926c56813f9d562a8
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev && rm -rf /var/lib/apt/lists/*
RUN python3 -c "import urllib.request; urllib.request.urlretrieve('https://github.com/eprover/eprover/archive/refs/tags/E-${E_VERSION}.tar.gz', '/tmp/e.tgz')" \
 && echo "${E_SHA256}  /tmp/e.tgz" | sha256sum -c - \
 && mkdir /src && tar xzf /tmp/e.tgz -C /src --strip-components=1 \
 && cd /src && ./configure && make -j"$(nproc)" rebuild \
 && /src/PROVER/eprover --version

# ---- Vampire, built from source (BSD-3): tag v5.1.0 pinned by commit; submodules viras and cadical at the
# commits that tag records; the optional z3 submodule is left out
FROM docker.io/library/python:3.13.18-slim AS vampire
ARG V_COMMIT=7b2f410ec4430c26217a85db62cf0c4a97042f8d
RUN apt-get update && apt-get install -y --no-install-recommends g++ cmake make git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone -q https://github.com/vprover/vampire /src && cd /src && git checkout -q ${V_COMMIT} \
 && git submodule update -q --init viras cadical \
 && cmake -S /src -B /build -DCMAKE_BUILD_TYPE=Release \
 && cmake --build /build -j"$(nproc)" \
 && cp "$(find /build -maxdepth 2 -type f -name 'vampire*' -perm -u+x | head -1)" /usr/local/bin/vampire \
 && /usr/local/bin/vampire --version

# ---- Prover9 / Mace4 (LADR, maintained fork github.com/AlgorithmicTruth/Prover9, GPL-2.0), tag LADR-2026-8A
FROM docker.io/library/python:3.13.18-slim AS ladr
ARG LADR_COMMIT=62ae6ff62fbe85b12c69d8625db1d358973c3d2f
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone -q https://github.com/AlgorithmicTruth/Prover9 /src && cd /src && git checkout -q ${LADR_COMMIT} \
 && make -j"$(nproc)" all \
 && ls bin && cp bin/prover9 bin/mace4 /usr/local/bin/ && (prover9 --version 2>&1 | head -3 || true)

# ---- Twee (BSD-3), unit-equality prover, from Hackage at a pinned index state; GHC 9.6.6
FROM docker.io/library/haskell:9.6.6-slim-bullseye AS twee
ARG TWEE_VERSION=2.7.1
ARG HACKAGE_INDEX=2026-10-01T00:00:00Z
RUN cabal update "hackage.haskell.org,${HACKAGE_INDEX}" \
 && cabal install --index-state="${HACKAGE_INDEX}" --install-method=copy --installdir=/out --ghc-options=-rtsopts \
      "twee-${TWEE_VERSION}" \
 && /out/twee --version 2>&1 | head -2; ldd /out/twee

FROM docker.io/library/python:3.13.18-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgmp10 libffi8 && rm -rf /var/lib/apt/lists/*
COPY --from=twee /out/twee /usr/local/bin/twee
COPY --from=vampire /usr/local/bin/vampire /usr/local/bin/vampire
COPY --from=ladr /usr/local/bin/prover9 /usr/local/bin/mace4 /usr/local/bin/
COPY --from=eprover /src/PROVER/eprover /usr/local/bin/eprover
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
