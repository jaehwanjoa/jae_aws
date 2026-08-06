FROM public.ecr.aws/lambda/python:3.13

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

RUN pip install uv

CMD ["lambda_function.lambda_handler"]
