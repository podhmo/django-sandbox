# -*- coding:utf-8 -*-
import json
import django
from django.conf import settings


settings.configure(
    DEBUG=True,
    INSTALLED_APPS=[__name__]
)
django.setup()

from rest_framework import serializers


class Comment(object):
    def __init__(self, name, content):
        self.name = name
        self.content = content


class Article(object):
    def __init__(self, name, content, comments):
        self.name = name
        self.content = content
        self.comments = comments


class RenamedArticle(object):
    def __init__(self, title, article):
        self.title = title
        self.article = article

    def __getattr__(self, k):
        return getattr(self.article, k)

    @property
    def name(self):
        raise Exception("don't access this")


class CommentSerializer(serializers.Serializer):
    name = serializers.CharField()
    content = serializers.CharField()


class ArticleSerializer(serializers.Serializer):
    name = serializers.CharField()
    content = serializers.CharField()
    comments = CommentSerializer(many=True)


if __name__ == "__main__":
    name = "hello"
    content = "hello world"
    comments = [Comment("title{}".format(i), "hmm") for i in range(3)]
    article = Article(name, content, comments)
    # print(json.dumps(ArticleSerializer(article).data, indent=2))

    serializer = ArticleSerializer(RenamedArticle("hai", article))
    print(type(serializer.fields["name"]), serializer.fields["name"], serializer.fields["name"].source)

    # Field(<>, source="title")
    # => field.source_attrs = ["title"]  # Field.bind()
    serializer.fields["name"].source_attrs = ["title"]

    print(type(serializer.fields["name"]), serializer.fields["name"], serializer.fields["name"].source)
    print(json.dumps(serializer.data, indent=2))
