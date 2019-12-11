FROM zerobell/mecab-ko:latest

RUN apt update

RUN apt -y install python3 git python3-pip

RUN pip3 install flask flask-restful

WORKDIR /workspace/mecab-src/
RUN git clone https://bitbucket.org/eunjeon/mecab-python-0.996.git
WORKDIR /workspace/mecab-src/mecab-python-0.996
RUN python3 setup.py build
RUN python3 setup.py install

RUN apt remove -y git

WORKDIR /
COPY . /app

EXPOSE 7946

WORKDIR /app
CMD ["python3", "app.py"]
