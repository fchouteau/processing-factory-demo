FROM python:3.7
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY pesto_cli-1.0.0-py3-none-any.whl /app
RUN python3 -m pip install /app/*.whl
RUN python3 -m pip install -r requirements.txt
COPY streamlit_app.py /app/
COPY pesto_streamlit /app/pesto_streamlit
COPY README.md /app/

CMD ["streamlit", "run", "streamlit_app.py"]
