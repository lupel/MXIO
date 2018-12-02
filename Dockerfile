FROM python:3.6 AS builder
WORKDIR /app
COPY . .
RUN python setup.py sdist bdist_wheel

FROM python:3.6-alpine AS runner
WORKDIR /app

ENV USER mortal
RUN adduser -u 1000 -s /bin/false -D -H $USER && \
    chown -Rv $USER:$USER /app && \
    pip install --upgrade pip

COPY --from=builder /app/dist/*.whl .
RUN for i in *.whl; do pip install $i; done

USER $USER
ENTRYPOINT [ "modbus-slave" ]
