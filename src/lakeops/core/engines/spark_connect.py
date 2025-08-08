from .spark import SparkEngine


class SparkConnectEngine(SparkEngine):
    def __init__(self, remote_host: str = 'sc://localhost'):
        from pyspark.sql import SparkSession
        spark_session = SparkSession.builder.remote(remote_host).getOrCreate()
        super().__init__(spark_session)
