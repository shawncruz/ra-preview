FROM public.ecr.aws/lambda/python:3.9

RUN bash -c 'echo -e ${LAMBDA_TASK_ROOT}'

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Install git
RUN yum -y install git

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .

RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handle" ]