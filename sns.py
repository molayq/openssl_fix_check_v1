import logging
import boto3
from botocore.exceptions import ClientError


# AWS_REGION = 'us-east-1'
# AWS_ACCESS_KEY = 'AKIASBT35K5SXIFP47XD'
# AWS_SECRET_KEY = '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'
# AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:140920051557:fix_connection_tls_check'
#
# # logger config
# logger = logging.getLogger()
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s: %(levelname)s: %(message)s')
#
# sns_client = boto3.client('sns', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
#                           aws_secret_access_key=AWS_SECRET_KEY, verify=False)


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

class SnsHelper:
    AWS_REGION = 'us-east-1'
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:140920051557:fix_connection_tls_check'

    @staticmethod
    def authenticate(access, secret):
        sns_client = boto3.client('sns', region_name=SnsHelper.AWS_REGION, aws_access_key_id=access,
                                  aws_secret_access_key=secret, verify=False)

        return sns_client

    @staticmethod
    def publish_message(authentication, topicArn, message, subject):
        try:

            response = authentication.publish(
                TargetArn=topicArn,
                Message=message,
                Subject=subject,
            )['MessageId']

        except ClientError:
            logger.exception(f'Could not publish message to the topic.')
            raise
        else:
            return response

    @staticmethod
    def trigger(access, secret, subject, message):
        topic_arn = SnsHelper.AWS_SNS_TOPIC
        authentication = SnsHelper.authenticate(access, secret)

        logger.info(f'Publishing message to topic - {topic_arn}...')
        message_id = SnsHelper.publish_message(authentication, topic_arn, str(message), subject)
        logger.info(
            f'Message published to topic - {topic_arn} with message Id - {message_id}.'
        )
