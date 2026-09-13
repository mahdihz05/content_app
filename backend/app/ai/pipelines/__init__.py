from importlib import import_module


_PIPELINES = {
    'ApprovalPipeline': '.create_content.approval_pipeline',
    'BasicInfoPipeline': '.create_content.basic_info_pipeline',
    'CampaignPipeline': '.create_content.campaign_pipeline',
    'CreateContentCore': '.create_content.core',
    'FinalPipeline': '.create_content.final_pipeline',
    'KeywordsPipeline': '.create_content.keyword_pipline',
    'KnowledgePipeline': '.create_content.knowledge_pipeline',
    'OutlinePipeline': '.create_content.outlne_pipeline',
    'ProductionInfoPipeline': '.create_content.production_info_pipeline',
    'ResearchPipeline': '.create_content.research_pipeline',
}

__all__ = list(_PIPELINES)


def __getattr__(name):
    module_name = _PIPELINES.get(name)
    if module_name is None:
        raise AttributeError(name)
    return getattr(import_module(module_name, __name__), name)
