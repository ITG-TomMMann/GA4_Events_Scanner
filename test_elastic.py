from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://72a4ae68f13d49d3900675dde16a6dcb.europe-west2.gcp.elastic-cloud.com:443",
    basic_auth=("elastic", "sELOzwrmXe3NY3ieBNBtNOr0")
)

print(es.info())
