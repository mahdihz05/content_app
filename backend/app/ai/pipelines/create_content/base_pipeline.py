# ai/pipelines__/base_pipeline.py

class BasePipeline:

    def run(self, context):
        raise NotImplementedError("Pipeline must implement run() method")
