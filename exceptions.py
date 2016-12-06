# -*- coding: utf-8 -*-
__author__ = 'Passion'


class WechatSogouException(Exception):
    """基于搜狗搜索的的微信公众号爬虫接口  异常基类
    """
    pass


class WechatSogouVcodeException(WechatSogouException):
    """基于搜狗搜索的的微信公众号爬虫接口 出现验证码 异常类
    """
    pass