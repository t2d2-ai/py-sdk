"""S3 Client Class"""
# pylint: disable=W0718, C0103
import os
from urllib.parse import urlparse

import boto3
from tqdm import tqdm

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")


def sizeof_fmt(num, suffix="B"):
    """Convert file sizes to human readable format"""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Y{suffix}"


class S3Client(object):
    """S3 Client with helper methods to operate on buckets and objects"""

    def __init__(self, AccessKey=AWS_ACCESS_KEY_ID, SecretKey=AWS_SECRET_ACCESS_KEY):
        """Initialize downloader"""
        self.s3 = boto3.resource(
            "s3", aws_access_key_id=AccessKey, aws_secret_access_key=SecretKey
        )

    def download_file(
        self, bucket=None, obj=None, url="s3://mybucket/myfile", filename="./myfile"
    ):
        """Download object from url"""
        if not (bucket or obj):
            # parse bucket/object key from provided url
            result = urlparse(url)
            bucket = result.netloc.split(".")[0]
            obj = result.path[1:]

        s3_bucket = self.s3.Bucket(bucket)  # type: ignore
        s3_bucket.download_file(obj, filename)

    def upload_file(self, path_to_file, bucket_name, obj_key, ACL="public-read"):
        """Upload file to S3"""
        bucket = self.s3.Bucket(bucket_name)  # type: ignore
        bucket.upload_file(path_to_file, obj_key, {"ACL": ACL})
        return

    def calculate_sizes(self, bucket_name, prefix):
        """Calculate count and size of objects"""
        bucket = self.s3.Bucket(bucket_name)  # type: ignore
        objects = bucket.objects.filter(Prefix=prefix)
        count, total_size = 0, 0
        for obj in tqdm(objects):
            count += 1
            total_size += obj.size
        result = {"number": count, "size": sizeof_fmt(total_size)}
        return result
