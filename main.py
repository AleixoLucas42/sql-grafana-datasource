from flask import Flask, jsonify, abort, render_template_string
import yaml
import datetime
import os
from tabulate import tabulate
import logging
import oracledb
import pyodbc
import psycopg2
from flasgger import Swagger
from dotenv import load_dotenv

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlserver").lower()
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

if DB_TYPE == "oracle":
    dsn = os.getenv("DB_DSN")
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_7")

elif DB_TYPE == "sqlserver":
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")

elif DB_TYPE == "postgres":
    host = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    port = os.getenv("DB_PORT", "5432")

else:
    raise ValueError("Invalid DB_TYPE. Use 'oracle', 'sqlserver' or 'postgres'.")

resume = [
    ("Database type", DB_TYPE),
    ("Database user", username),
    (
        "Database password",
        password if os.getenv("LOG_LEVEL", "INFO") == "DEBUG" else "*************",
    ),
    ("Database host", os.getenv("DB_SERVER", "N/A")),
    ("Database name", database if DB_TYPE != "oracle" else dsn),
    ("Log level", os.getenv("LOG_LEVEL", "INFO")),
    ("Start time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
]

app = Flask(__name__)
swagger = Swagger(app)


def load_queries(file_path="/app/queries.yaml"):
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


queries = load_queries()


@app.route("/queries", methods=["GET"])
def list_queries():
    """
    List all available queries.
    ---
    responses:
      200:
        description: A list of available queries
        schema:
          type: object
          properties:
            available_queries:
              type: array
              items:
                type: string
    """
    query_names = list(queries.get("sqlgd", {}).keys())
    return jsonify({"available_queries": query_names})


@app.route("/")
def home():
    logging.info(f"Showing App Config")
    table = tabulate(resume, tablefmt="fancy_grid")
    return render_template_string(
        """
        <html>
            <body>
                <h2>App Status</h2>
                <pre>{{ table }}</pre>
            </body>
        </html>
    """,
        table=table,
    )


def execute_oracle_query(query):
    with oracledb.connect(user=username, password=password, dsn=dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def execute_sqlserver_query(query):
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    with pyodbc.connect(conn_str) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def execute_postgres_query(query):
    with psycopg2.connect(
        host=host, database=database, user=username, password=password, port=port
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


@app.route("/query/<string:query_name>", methods=["GET"])
def execute_query(query_name):
    """
    Execute a query by name.
    ---
    parameters:
      - name: query_name
        in: path
        type: string
        required: true
        description: The name of the query to execute.
    responses:
      200:
        description: Query executed successfully
        schema:
          type: object
          properties:
            query:
              type: string
            results:
              type: array
              items:
                type: array
                items:
                  type: string
      404:
        description: Query not found
      500:
        description: Error executing query
    """
    logging.info(f"Querying {query_name}")
    query_group = queries.get("sqlgd", {})
    if query_name not in query_group:
        message = f"Query '{query_name}' not found in YAML file."
        logging.warning(message)
        abort(404, description=message)

    query = query_group[query_name][0]

    try:
        if DB_TYPE == "oracle":
            results = execute_oracle_query(query)
        elif DB_TYPE == "sqlserver":
            results = execute_sqlserver_query(query)
        elif DB_TYPE == "postgres":
            results = execute_postgres_query(query)
        else:
            abort(500, description="Unsupported database type.")

        return jsonify({"query": query, "results": [list(row) for row in results]})

    except Exception as e:
        logging.error(f"error: {str(e)} Querying {query_name}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
