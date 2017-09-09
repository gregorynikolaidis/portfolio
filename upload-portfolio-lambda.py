import boto3
import io
import zipfile
import mimetypes


def lambda_handler(event, context):
    # TODO implement

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:032631690801:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')


        portfolio_bucket = s3.Bucket('portfolio.gregorynikolaidis.info')
        build_bucket = s3.Bucket('portfoliobuild.gregorynikolaidis.info')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject='Portfolio Deployed', Message='Portfolio Deployed Successfully!')
        print("Deployment Done!")
    except:
        topic.publish(Subject='Portfolio Delopyment Failed', Message='Portfolio Deployement Failed!')
        raise
    return ("hello world")
