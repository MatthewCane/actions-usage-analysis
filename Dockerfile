FROM python:3.12-slim-bookworm

COPY actions_usage_analysis.py requirements.txt /app/

WORKDIR /app/

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "actions_usage_analysis.py"]
