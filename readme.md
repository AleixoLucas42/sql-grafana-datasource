## SQL Grafana Datasource

This is an simple SQL query exporter developed to be used with an Grafana plugin wich allow us to get http rest responses,
for example [`Infinity`](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) datasource plugin.

## How it works
After you configure `queries.yaml` file, execute the application, then, application is going to load queries from queries file.
Afer that, the application expose an http endpoint, so you can check routes on [`/apidocs`](http://localhost:5000/apidocs). To get an query result, you have to 
use the path `/query/<query-name-configured-on-file>`.

## Queries file example
To get result for `list_tables` query, you can access `/query/list_tables`.
```yaml
sqlgd:
  list_tables:
    - SELECT table_name FROM user_tables
  database_version:
    - SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'
  complex_query:
    - |
      Multiline
      Complex
      Query
      EXAMPLE
```

## Example running with docker
```bash
# SQL Server
docker run -v ./queries.yaml:/app/queries.yaml \
  -p 5000:5000 \
  -e DB_TYPE="sqlserver" \
  -e DB_USERNAME="user" \
  -e DB_PASSWORD="password" \
  -e DB_SERVER=="10.11.12.13" \
  -e DB_DATABASE="database" \
  aleixolucas/sql-grafana-datasource

# POSTGRES
docker run -v ./queries.yaml:/app/queries.yaml \
  -p 5000:5000 \
  -e DB_TYPE="postgres" \
  -e DB_USERNAME="user" \
  -e DB_PASSWORD="password" \
  -e DB_SERVER="10.11.12.13"\
  -e DB_DATABASE="database" \
  aleixolucas/sql-grafana-datasource

# ORACLE
docker run -v ./queries.yaml:/app/queries.yaml \
  -p 5000:5000 \
  -e DB_TYPE="oracle" \
  -e DB_DSN="10.11.12.13:1521/database" \
  -e DB_USERNAME="user" \
  -e DB_PASSWORD="password" \
  aleixolucas/sql-grafana-datasource
```
Example with **kubernetes** [here](./kubernetes/)

## Environment variables
### Global
| Variable    | Required | Example                  |
| :---------- | :------: | -----------------------: |
| LOG_LEVEL   |   False  | INFO,WARNING,ERROR,DEBUG |
#### SQL SERVER
| Variable    | Required | Example          |
| :---------- | :------: | ---------------: |
| DB_TYPE     |   True   | sqlserver        |
| DB_USERNAME |   True   | sa               |
| DB_PASSWORD |   True   | s3Cur3_P@$$w0rd  |
| DB_SERVER   |   True   | 10.11.12.13      |
| DB_DATABASE |   True   | PRODUCTION_SALES |

#### POSTGRES
| Variable    | Required | Example          |
| :---------- | :------: | ---------------: |
| DB_TYPE     |   True   | postgres         |
| DB_USERNAME |   True   | postgres         |
| DB_PASSWORD |   True   | s3Cur3_P@$$w0rd  |
| DB_SERVER   |   True   | 10.11.12.13      |
| DB_DATABASE |   True   | PRODUCTION_SALES |
| DB_PORT     |   False  | 5432             |

#### ORACLEDB
| Variable    | Required | Example          |
| :---------- | :------: | ---------------: |
| DB_TYPE     |   True   | oracle           |
| DB_USERNAME |   True   | best_user_ever   |
| DB_PASSWORD |   True   | s3Cur3_P@$$w0rd  |
| DB_DSN      |   True   | 10.11.12.12:1521/PRODUCTION_SALES |

## Curl example
![example](./assets/img/example.png)

# Setup on Grafana
- Install Infinity plugin from Grafana Labs
- Add new datasouce, leave default configuration
- On a dashboard, add a panel
- Select infinity datasource plugin
- Set type to JSON, method as GET, Source as URL, Format as Table and Method as GET
- Fill the url box with your query url, example: `http://10.11.12.14:5000/query/database_version`
- Set Grafana visualization from `Time Series` to `Table`

### Troubleshooting
Troubleshooting can be done by checking logs and set environment variable LOG_LEVEL to DEBUG also<br>
In the root url, you can check your configurations, the password is going to appear when DEBUG is set.<br>
![status](./assets/img/status.png)
