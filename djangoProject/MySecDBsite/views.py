from django.shortcuts import render, redirect
from django.contrib import messages
from django_tables2 import RequestConfig
from collections import defaultdict
import mariadb
import pyodbc
import timeit
from .tables import NameTable
from .dbconnector import MariadbConnector, RedshiftConnector


# Main page render
def index(request):
    return render(request, 'home.html')


# Instacart page render
def search_form(request):
    connector = MariadbConnector.get_connected()
    connector.connect(database="instacart", ini=True)
    rconnector = RedshiftConnector.get_connected()
    rconnector.connect(ini=True)
    return render(request, 'text_submit.html', {'table': None})


# Instacart query process
def search_text(request):
    global alexa_result
    global alexa_time
    # choose mariadb to query 
    if request.GET['slc'] == 'rds':
        connector = MariadbConnector.get_connected()
        # timer start
        start_time = timeit.default_timer()
        if connector.connect(database="instacart", ini=True):
            # check if the input is empty
            if 'txt' in request.GET and request.GET['txt']:
                connector.set_query(request.GET['txt'])
                result = connector.perform_query(database="instacart")
                alexa_result = result
                if isinstance(result, list) and result:
                    # render table
                    table = NameTable(result)
                    # activate sorting by head
                    RequestConfig(request).configure(table)
                    # set pagination
                    table.paginate(page=request.GET.get("page", 1), per_page=25)
                elif isinstance(result, int):
                    messages.success(request, f"Database changed.\nAffected rows = {result}")
                    return redirect('instacart')
                else:
                    messages.error(request, f"Invalid query or no record matched.{result}")
                    return redirect('instacart')
            else:
                messages.warning(request, "Your query is empty.")
                return redirect('instacart')
        else:
            messages.error(request, "Connection failed...")
            return redirect('instacart')
        total_time = 1000 * (timeit.default_timer() - start_time)
        alexa_time = round(total_time, 3)
        messages.info(request, "Query finished. Query time = %.3f ms" % round(total_time, 3))
        return render(request, 'text_submit.html', {'table': table})
    # choose redshift to query
    elif request.GET['slc'] == 'redshift':
        connector = RedshiftConnector.get_connected()
        start_time = timeit.default_timer()
        if connector.connect():
            if 'txt' in request.GET and request.GET['txt']:
                connector.set_query(request.GET['txt'])
                result = connector.perform_query()
                if isinstance(result, list) and result:
                    table = NameTable(result)
                    RequestConfig(request).configure(table)
                    table.paginate(page=request.GET.get("page", 1), per_page=25)
                elif isinstance(result, int):
                    messages.success(request, f"Database changed.\nAffected rows = {result}")
                    return redirect('instacart')
                else:
                    connector.rollback()
                    messages.error(request, f"Invalid query or no record matched.{result}")
                    return redirect('instacart')
            else:
                messages.warning(request, "Your query is empty.")
                return redirect('instacart')
        else:
            messages.error(request, "Connection failed...")
            return redirect('instacart')
        total_time = 1000 * (timeit.default_timer() - start_time)
        messages.info(request, "Query finished. Query time = %.3f ms" % round(total_time, 3))
        return render(request, 'text_submit.html', {'table': table})
    return redirect('instacart')


# ABC_Retail page render
def search_form_abc(request):
    connector = MariadbConnector.get_connected()
    connector.connect(database="ABC_Retail", ini=True)
    return render(request, 'text_submit2.html', {'table': None})


# ABC_Retail query process, without Redshift
def search_text_abc(request):
    connector = MariadbConnector.get_connected()
    start_time = timeit.default_timer()
    if connector.connect(database="ABC_Retail"):
        if 'txt' in request.GET and request.GET['txt']:
            connector.set_query(request.GET['txt'])
            result = connector.perform_query(database="ABC_Retail")
            if isinstance(result, list) and result:
                table = NameTable(result)
                RequestConfig(request).configure(table)
                table.paginate(page=request.GET.get("page", 1), per_page=25)
            elif isinstance(result, int):
                messages.success(request, f"Database changed.\nAffected rows = {result}")
                return redirect('abc-retail')
            else:
                messages.error(request, f"Invalid query or no record matched.{result}")
                return redirect('abc-retail')
        else:
            messages.warning(request, "Your query is empty.")
            return redirect('abc-retail')
    else:
        messages.error(request, "Connection failed...")
        return redirect('abc-retail')
    total_time = 1000 * (timeit.default_timer() - start_time)
    messages.info(request, "Query finished. Query time = %.3f ms" % round(total_time, 3))
    return render(request, 'text_submit2.html', {'table': table})


alexa_result = None
alexa_time = -1
def alexa_query(request):
    alexa_table = None
    if isinstance(alexa_result, list) and alexa_result:
        alexa_table = NameTable(alexa_result)
        RequestConfig(request).configure(alexa_table)
        alexa_table.paginate(page=request.GET.get("page", 1), per_page=25)
        messages.info(request, "Query finished. Query time = %.3f ms" % alexa_time)
    elif isinstance(alexa_result, int):
        messages.success(request, f"Database changed.\nAffected rows = {alexa_result}")
    else:
        messages.error(request, f"Invalid query.{alexa_result}")
    return render(request, 'alexa.html', {'table': alexa_table})