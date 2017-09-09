import boto3
import io
import zipfile
import mimetypes


def lambda_handler(event, context):
    # TODO implement

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:032631690801:deployPortfolioTopic')

    location = {
        "bucketName": 'portfoliobuild.gregorynikolaidis.info',
        "objectKey": 'portfoliobuild.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print("Building portfolio from " + str(location))

        s3 = boto3.resource('s3')


        portfolio_bucket = s3.Bucket('portfolio.gregorynikolaidis.info')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject='Portfolio Deployed', Message='Portfolio Deployed Successfully!')
        print("Deployment Done!")

        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject='Portfolio Delopyment Failed', Message='Portfolio Deployement Failed!')
        raise
    return ("hello world")

    
