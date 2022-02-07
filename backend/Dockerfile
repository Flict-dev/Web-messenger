FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /aap
COPY app .
COPY requirements.txt ./requirements.txt
EXPOSE 80
ENV IS_IN_DOCKER=true

RUN pip3 install -r requirements.txt
RUN python ./db/init_tables.py

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
