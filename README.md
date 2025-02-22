# cdc-ddb
CDC from DynamoDB

## Scripts

 ```shell
 chmod +x create_ddb.sh
 ./create_ddb.sh
 ```

 ```shell
 chmod +x load_data_ddb.sh
 ./load_data_ddb.sh
 ```


## Environment
Execute from an AWS profile

## Sources
scripts -> shells to create DynamoDB tables and ingest raws.

## Architecture
![Arquitectura](/assets/arquitectura.png)

## Config AWS Services

### Kinesis DS
![Kinesis DS](/assets/config_kinesis_data_stream.png)

### Kinesis Firehose
![kinesis Firehose](/assets/kinesis_firehose.png)\

### S3
![S3](/assets/s3.png)

### Glue Crawler
![Glue Crawler](/assets/crawler.png)

### Glue Catalog
![Glue Catalog](/assets/glue_catalog.png)

### Athena
![Athena](/assets/athena.png)

## DDL Table:

 ```sql
`CREATE EXTERNAL TABLE dev_test_cdc_s3(
  awsregion string COMMENT 'from deserializer', 
  eventid string COMMENT 'from deserializer', 
  eventname string COMMENT 'from deserializer', 
  useridentity string COMMENT 'from deserializer', 
  recordformat string COMMENT 'from deserializer', 
  tablename string COMMENT 'from deserializer', 
  dynamodb struct<approximatecreationdatetime:bigint,keys:struct<transaction_id:struct<s:string>,timestamp:struct<n:string>>,newimage:struct<amount:struct<n:string>,currency:struct<s:string>,transaction_id:struct<s:string>,payment_method:struct<s:string>,status:struct<s:string>,timestamp:struct<n:string>>,sizebytes:int> COMMENT 'from deserializer', 
  eventsource string COMMENT 'from deserializer')
PARTITIONED BY ( 
  partition_0 string, 
  partition_1 string, 
  partition_2 string, 
  partition_3 string)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='awsRegion,dynamodb,eventID,eventName,eventSource,recordFormat,tableName,userIdentity') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://dev-test-cdc-s3/'
TBLPROPERTIES (
  'CrawlerSchemaDeserializerVersion'='1.0', 
  'CrawlerSchemaSerializerVersion'='1.0', 
  'UPDATED_BY_CRAWLER'='dev-test-cdc-cw', 
  'averageRecordSize'='591', 
  'classification'='json', 
  'compressionType'='none', 
  'objectCount'='4', 
  'partition_filtering.enabled'='true', 
  'recordCount'='200', 
  'sizeKey'='118257', 
  'typeOfData'='file')`
 ```