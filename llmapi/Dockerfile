FROM python:3.9

WORKDIR /llmapi

COPY ./requirements.txt /llmapi/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /llmapi/requirements.txt

COPY ./ /llmapi/

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
