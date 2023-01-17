deploy:
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com
	docker build -t ra-preview . --platform=linux/amd64
	docker tag ra-preview:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/ra-preview:latest
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/ra-preview:latest