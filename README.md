# opera-egis

1. Build lambda deployment package. See https://github.com/lambgeo/docker-lambda?tab=readme-ov-file#2-advanced-need-other-dependencies
   ```
   docker build --tag package:latest .
   docker run --name lambda -w /var/task -itd package:latest bash
   docker cp lambda:/tmp/package.zip package.zip
   docker stop lambda
   docker rm lambda
   ```

1. Deploy the cloudformation template
   ```
   aws s3 cp package.zip s3://asj-dev/cloudformation/
   aws cloudformation deploy --stack-name <stack name> --template-file cloudformation.yml --capabilities CAPABILITY_IAM --parameter-overrides Username=<edl username> Password=<edl password> BucketName=<bucket name>
   ```

1. Submit jobs for all urls in `data/opera_urls.txt.zip`
   ```
   unzip data/opera_urls.txt.zip
   python submit_jobs.py
   ```
