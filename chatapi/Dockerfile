FROM python:3.9

WORKDIR /chatapi

COPY ./requirements.txt /chatapi/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /chatapi/requirements.txt

COPY . /chatapi/

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
