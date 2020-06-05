FROM python:3.8.1

WORKDIR /user/src/app

COPY './requirements.txt' .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 2222 80

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "-p 80"]