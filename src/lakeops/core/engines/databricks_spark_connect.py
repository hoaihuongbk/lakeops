from databricks.connect import DatabricksSession

from .spark import SparkEngine


class DatabricksSparkConnectEngine(SparkEngine):
    def __init__(self, profile_name: str = "DEFAULT"):
        builder = DatabricksSession.builder
        if profile_name != "DEFAULT":
            builder = builder.profile(profile_name)
        builder = builder.serverless()
        spark_session = builder.getOrCreate()
        super().__init__(spark_session)
