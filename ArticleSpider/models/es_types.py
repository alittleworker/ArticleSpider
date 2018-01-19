# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    #jobbole文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url_object_id = Keyword()
    url = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    creat_date = Date()
    praise_num = Integer()
    collect_num = Integer()
    comment_num = Integer()
    content = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")

    class Meta:
        index = "jobbole"
        doc_type = "article"

if __name__=="__main__":
    ArticleType.init()