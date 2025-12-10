FROM python:3.9

WORKDIR /authapi

COPY ./requirements.txt /authapi/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /authapi/requirements.txt

COPY ./ /authapi/

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
