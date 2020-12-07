import django_tables2 as tables
from .models import Person
import datetime


# Table render, dynamically add column according to the query result
class NameTable(tables.Table):
    def __init__(self, *args, **kwargs):
        self.base_columns.clear()
        for k in args[0][0].keys():
            # check if the data type is datetime, then format the result
            if isinstance(args[0][0][k], datetime.datetime):
                self.base_columns[k] = tables.DateTimeColumn(orderable=True, format='Y-m-d, H:i:s.u')
            else:
                self.base_columns[k] = tables.Column(orderable=True)
        super().__init__(*args, **kwargs)

    class Meta:
        # theme of table
        attrs = {"class": "table table-bordered table-striped table-dark table-sm"}
