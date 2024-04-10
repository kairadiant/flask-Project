# Queens College
# Database Systems (CSCI 331)
# Winter 2024
# Utility class to support db applications
# Kayla Washington

import pymysql
import time
import texttable
import OutputUtil as ou
import json

db = "udb"
assn = None


def get_password():
    with open('password.txt', 'r') as file:
        return file.read().strip()


password = get_password()
user = "Kayla"


def list_db_data(cursor, sql, desc):
    cursor.execute(sql)
    results = [row[0] for row in cursor]
    print(desc + ":", results)
    return results


def log_query(query_text, query_desc, query_db, query_rows, query_user, query_assn, query_dur, conn=None):
    query_text = query_text.replace("'", "\\'")
    query = f"INSERT into query (query_text, query_desc, query_db, query_rows, query_user, query_assn, query_dur) \nvalues ('{query_text} ', '{query_desc}','{query_db}',{query_rows}, '{query_user}', '{query_assn}', {query_dur})"
    new_conn = False
    if conn is None:
        new_conn = True
        conn = pymysql.connect(host="localhost", user="root", passwd=get_password(), db="udb")
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    if new_conn:
        conn.close()


def call_procedure(query_text, cursor):
    proc_query = query_text[4:].strip()
    idx1 = proc_query.index('(')
    idx2 = proc_query.index(')')
    arg = int(proc_query[idx1 + 1: idx2])
    proc = proc_query[:idx1]
    print(f"PROC QUERY {proc}")
    cursor.callproc(proc, (arg,))


def run_query(query_text, query_desc, query_db, assignment, query_execute_values=None, get_cursor_desc=False):
    query_src = assignment
    conn = pymysql.connect(host="localhost", user="root", passwd=password, db=query_db)
    start = time.time()
    cursor = conn.cursor()
    if query_text.upper().startswith("CALL"):
        call_procedure(query_text, cursor)
    else:
        if query_execute_values is None:
            cursor.execute(query_text)
        else:
            cursor.execute(query_text, query_execute_values)
    end = time.time()
    duration = end - start
    conn.commit()
    log_query(query_text, query_desc, query_db, len(rows), user, query_src, duration)
    conn.close()
    query_upper = query_text.upper()
    if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESC"):
        headers = [desc[0] for desc in cursor.description]
        if len(rows) == 0:
            data = [[None for _ in headers]]
        else:
            data = [[col for col in row] for row in rows]

        if get_cursor_desc:
            return headers, data, cursor.description
        else:
            return headers, data
    else:
        return [], []


def print_table(title, headers, data, alignments=None):
    if alignments is None:
        alignments = ['l'] * len(headers)
    tt = texttable.Texttable(0)
    tt.set_cols_align(alignments)
    tt.add_rows([headers] + data, header=True)
    print(title)
    print(tt.draw())
    print()


def retrieve_query_log(assignments, db):
    tables = []
    for assignment in assignments:
        sql = f"select * from query where query_assn = '{assignment}'"
        desc = f"Retrieve all queries executed for assignment {assignment}"
        headers, data = run_query(sql, desc, db, assignments[-1])
        alignments = ["l"] * len(headers)
        types = ["S"] * len(headers)
        table = [desc, headers, types, alignments, data]
        tables.append(table)
    output_file = assignment.replace(" ", "") + "-query-history.html"
    title = "All queries for assignments to date"
    ou.write_html_file_new(output_file, title, tables, True, None, True)


# [1] Define a function get_ruler(length) that will create a "ruler" (i.e. numeric column headings) used to measure the positions and total space, something like:
def get_ruler_for_html(length):
    ruler1 = "".join([str(10 * i).rjust(10, ' ') for i in range(1, 2 + int(length / 10))])
    ruler1 = ruler1.replace(' ', '&nbsp;')
    ruler2 = "0123456789" * (1 + int(length / 10))
    return ruler1 + "<br>>" + ruler2


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_number(x):
    return isinstance(x, int) or isinstance(x, float) or (isinstance(x, str) and is_float(x))


def process_queries(comments, queries, db, assignment, format=""):
    tables = []
    for i in range(len(queries)):
        query = queries[i]
        comment = comments[i]
        try:
            if format in ["F", "V"]:
                headers, data, cursor_desc = run_query(query, comment, db, assignment, None, True)
                add_formatted_data(cursor_desc, data, format, headers)
            else:
                headers, data = run_query(query, comment, db, assignment)
            if len(headers) == 0:
                continue
            # check if data returned is a numbers column or not
            numeric = [all([is_number(data[i][j]) for i in range(len(data))]) for j in range(len(data[0]))]
            types = ["N" if numeric[j] else "S" for j in range(len(numeric))]
            alignments = ["r" if numeric[j] else "l" for j in range(len(numeric))]
            table = [comment, headers, types, alignments, data]
            tables.append(table)
        except Exception as e:
            print(f"Error processing query: {query}\nError: {e}\n\n")
    output_file = assignment.replace(" ", "") + ".html"
    title = f"All queries for '{assignment}'"
    ou.write_html_file_new(output_file, title, tables, True, None, True)


def add_formatted_data(cursor_desc, data, format, headers):
    headers.append(("Fixed" if format == "F" else "Variable") + "-Length Format")
    col_widths = [desc[3] for desc in cursor_desc]
    for row in data:
        if format == "F":
            record = "".join([str(row[i]) for i in range(len(col_widths))])
            record = record.replace(" ", "&nbsp;")
        else:
            record = "|".join([str(row[i]).ljust(col_widths[i], " ") for i in range(len(col_widths))])
        ruler = "<tt>" + get_ruler_for_html(sum(col_widths)) + "<br>" + record + "</tt>"
        row.append(ruler)


def read_queries(file_name):
    with open(file_name, "r") as file:
        comments = []
        sqls = []
        text = file.read()
        queries = text.strip().split(";")
        for query in queries:
            if len(query.strip()) == 0:
                continue
            if "*/" in query:
                comment, sql = query.split("*/", 1)
                comment = comment.replace("/*", "").strip()
            else:
                comment = f"Query from: '{file_name}'"
                sql = query
            sql = sql.strip()
            if "CREATE FUNCTION" in sql.upper() or "CREATE PROCEDURE" in sql.upper():
                sql = sql.replace("##", ";")
                print(f"REPLACED ## {sql}")
            comments.append(comment)
            sqls.append(sql)
        return comments, sqls


# [2c] Create a Python function to_json(headers, data) that converts the headers and data into JSON format
def to_json(title, headers, data):
    rows = []
    for i in range(len(data)):
        s = '{' + ', '.join(['"' + headers[j] + '":"' + str(data[i][j]) + '"' for j in range(len(headers))]) + '}'
        rows.append(s)
    return '{' + '"' + title + '":[\n' + ",\n".join(rows) + ']}'


# [2b] Create a Python function to_xml(headers, data) that converts the headers and data into XML format
def xml_clean(item):
    return str(item).replace("&", "&amp;")


def to_xml(title, headers, data):
    nl = "\n"
    headers = [header.replace(" ", "") for header in headers]
    x_header = '<?xml version="1.0" encoding="UTF-8"' + '?>'
    x_title = nl + ou.create_element("title", xml_clean(title))
    content = ""
    for row in data:
        x_items = nl + "".join([ou.create_element(headers[i], xml_clean(row[i])) for i in range(len(row))])
        x_row = ou.create_element("row", x_items)
        content += x_row
    x_body = nl + ou.create_element("root", x_title + content)
    xml = x_header + x_body
    return xml


# [2a] Create a Python function to_csv(headers, data) that converts the headers and data into CSV format
def to_csv(headers, data):
    s_headers = ','.join(headers)
    s_data = '\n'.join([",".join([str(col) for col in row]) for row in data])
    return s_headers + "\n" + s_data


# [4] Create a Python function backup_table(name) that will
#
# read the contents of the table using run_query
# determine the number of rows, i.e. len(data)
# determine the number of columns, i.e. len(headers)
# use to_csv() to convert the data to CSV
# use to_xml() to convert the data to XML
# use to_json() to convert the data to JSON
# insert this information into the new backup table.
#
# Note: due to space constraints, there may be issues with logging huge inserts into the existing query table.
def backup_table(name):
    query = f"Select * from {name}"
    desc = f"Retrieve rows from {name} for backup"
    headers, data = run_query(query, desc, db, assn)
    csv_data = to_csv(headers, data)
    xml_data = to_xml(name, headers, data)
    json_data = to_json(name, headers, data)
    query2 = f"INSERT into backup (relation, num_rows, num_cols,csv_length, xml_length, json_length, csv_data, xml_data, json_data) values ('{name}',{len(data)},{len(headers)},{len(csv_data)},{len(xml_data)},{len(json_data)}, '{csv_data}', '{xml_data}', '{json_data}')"
    desc2 = f"Save copy of table {name} in different formats"
    headers2, data2 = run_query(query2, desc2, db, assn)


# [5] Create a Python function restore_data(name, format) that will
#
# read the row of the latest backup of the table/relation name
# get the request format of that backup
# use from_csv() to convert the data from CSV back to headers and data
# use from_xml() to convert the data from XML back to headers and data
# use from_json() to convert the data from JSON back to headers and data
# makes an HTML page with the headers, and data for each of three format, each appropriately labeled (They should look similar as they were originally formed from the same data)
#
# A query to get the latest backup row for a given relation r is:
#
# SELECT * FROM backup where dtm = (SELECT MAX(dtm) FROM backup where relation = r);
def restore_data(name):
    query = f"SELECT * FROM backup where lower(relation) = '{name.lower()}' and dtm = (SELECT MAX(dtm) FROM backup where lower(relation) = '{name.lower()}')"
    desc = f"Retrieve the latest backup row for the table {name}"
    headers, data = run_query(query, desc, db, assn)
    headers_csv, data_csv = from_csv(data[0][7])
    headers_xml, data_xml = from_xml(data[0][8])
    headers_json, data_json = from_json(data[0][9], name)
    tables = []
    for pair in [(headers_csv, data_csv, "CSV"), (headers_xml, data_xml, "XML"), (headers_json, data_json, "JSON")]:
        headers, data, format = pair
        title = f"Restoration of data for table {name} in {format} format"
        numeric = [all([is_number(data[i][j]) for i in range(len(data))]) for j in range(len(data[0]))]
        types = ["N" if numeric[j] else "S" for j in range(len(numeric))]
        alignments = ["r" if numeric[j] else "l" for j in range(len(numeric))]
        table = [title, headers, types, alignments, data]
        tables.append(table)
    return tables


# [3a] Create a Python function from_csv(csv) that converts the csv into headers (1D) and data (2D)
def from_csv(csv):
    lines = csv.split("\n")
    headers = lines[0].split(",")
    data = [lines[1:][i - 1].split(",") for i in range(1, len(lines))]
    return headers, data


# [3b] Create a Python function from_xml(xml) that converts the xml into headers (1D) and data (2D)
def from_xml(xml):
    headers = []
    data = []
    idx_row = xml.find("<row>")
    while idx_row > 0:
        idx_endrow = xml.find("</row>", idx_row)
        row = xml[idx_row + 5:idx_endrow]
        elements = row.strip().split("\n")
        datum = []
        for element in elements:
            idx_begin_content = element.find(">") + 1
            idx_end_content = element.find("</")
            content = element[idx_begin_content: idx_end_content]
            datum.append(content)
            if len(headers) < len(elements):
                header = element[1:idx_begin_content - 1]
                headers.append(header)
        data.append(datum)
        idx_row = xml.find("<row>", idx_endrow)
    return headers, data


# [3c] Create a Python function from_json(json) that converts the json into headers (1D) and data (2D)
def from_json(json_text, name):
    json_data = json.loads(json_text)
    headers = []
    data = []
    do_headers = True
    for items in json_data[name]:
        row = []
        for item in items:
            row.append(items[item])
            if do_headers:
                headers.append(item)
        do_headers = False
        data.append(row)
    return headers, data


# SELECT product_name,
# SUM(CASE WHEN store_location = 'North' THEN num_sales ELSE 0 END) AS north,
# SUM(CASE WHEN store_location = 'Central' THEN num_sales ELSE 0 END) AS central,
# SUM(CASE WHEN store_location = 'South' THEN num_sales ELSE 0 END) AS south,
# SUM(CASE WHEN store_location = 'West' THEN num_sales ELSE 0 END) AS west
# FROM product_sales
# GROUP BY product_name;
def pivot_table(table, col_x, col_y, col_val):
    query = f"SELECT DISTINCT {col_x} from {table}"
    desc = f"Get all distinct values of {col_x} from table for pivot table"
    headers, data = run_query(query, desc, "udb", assn)

    query2 = f"SELECT {col_y}, "
    query2 += ",\n".join(
        f"SUM(CASE WHEN {col_x} = '{row[0]}' THEN {col_val} ELSE 0 END) AS {row[0].replace('.', '_').replace(' ', '')}"
        for row in data
    )
    query2 += f" FROM {table} GROUP BY {col_y}"

    desc2 = f"Build a pivot table {table} for {col_x}, {col_y}"
    headers2, data2 = run_query(query2, desc2, "udb", assn)

    numeric = [all([is_number(data2[i][j]) for i in range(len(data2))]) for j in range(len(data2[0]))]
    alignments = ["r" if numeric[j] else "l" for j in range(len(numeric))]
    types = ["N" if n else "S" for n in numeric]
    table = [desc2, headers2, types, alignments, data2]
    return table


def make_pivot_tables(examples, assn):
    html_tables = []
    for example in examples:
        html_tables += [pivot_table(example[0], example[1], example[2], example[3])]
    output_file = assn.replace(" ", "") + "-pivot-tables.html"
    title = "Pivot Tables for select examples"
    ou.write_html_file_new(output_file, title, html_tables, True, None, True)
