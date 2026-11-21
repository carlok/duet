# Isolated environment for the two-operation theory search. Free software only; versions pinned
# to the ones the cloud sessions used (z3 effort numbers depend on the z3 version).
FROM docker.io/library/python:3.13-slim
RUN pip install --no-cache-dir numpy==2.5.3 numba==0.68.1 z3-solver==5.4.1.0
WORKDIR /home/claude/soup
CMD ["bash", "run.sh"]
