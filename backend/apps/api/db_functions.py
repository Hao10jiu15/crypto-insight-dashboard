from django.db.models import Func, Aggregate, fields


class TimeBucket(Func):
    """
    一个自定义的Func表达式，用于在Django ORM中调用TimescaleDB的time_bucket函数。
    """

    function = "time_bucket"
    # 定义输出字段类型，对于时间戳，DateTimeField是合适的
    output_field = fields.DateTimeField()


class First(Aggregate):
    """
    一个自定义的聚合类，用于实现TimescaleDB的FIRST(value, time)聚合函数。
    """

    function = "FIRST"
    template = "%(function)s(%(expressions)s, time)"  # 定义SQL模板
    # 允许我们在聚合函数中指定排序
    allow_distinct = False


class Last(Aggregate):
    """
    一个自定义的聚合类，用于实现TimescaleDB的LAST(value, time)聚合函数。
    """

    function = "LAST"
    template = "%(function)s(%(expressions)s, time)"
    allow_distinct = False
