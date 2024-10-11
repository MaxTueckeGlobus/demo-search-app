# [36087] - Create a Search application using the SDK

Commands in ```search-cli.py```

```
create-index DISPLAY_NAME DESCRIPTION
delete-index INDEX_ID
delete-entry INDEX_ID SUBJECT
ingest INDEX_ID SUBJECT DATA_PATH --is-dir BOOL
search INDEX_ID QUERY_PATH  --offset INTEGER --limit INTEGER
search-entry INDEX_ID SUBJECT
whoami
logout
```

Commands run to create / populate / search demo index:
```
create-index test-search-index 'maxs test search index'
ingest e32c842e-df0d-42cb-9844-6af771505357 person ./ingest_data --is-dir true
search e32c842e-df0d-42cb-9844-6af771505357 ./queries/simple_query.json
search e32c842e-df0d-42cb-9844-6af771505357 ./queries/facet_query.json
```