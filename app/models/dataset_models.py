from pydantic import Field, BaseModel
from .base_models import APIResponse


class DatasetListResponse(APIResponse):
    """
    Dataset list response class
    """
    result: dict = Field({}, example={
   "code":200,
   "error_msg":"",
   "result":[
      {
         "id":33076,
         "labels":[
            "Dataset"
         ],
         "global_entity_id":"bc0da1cf-8e25-45d5-a440-bc67539055d3-1628795709",
         "creator":"admin",
         "modality":[
            
         ],
         "code":"dataset1testdata",
         "project_geid":"a0927b4f-8df2-4e74-84d4-ae5e3103bb3e-1628782564",
         "total_files":6,
         "description":"1",
         "source":"",
         "title":"DatasetTestData",
         "type":"GENERAL",
         "tags":[
            
         ],
         "license":"",
         "time_lastmodified":"2021-08-12T20:15:52",
         "size":6291456,
         "collection_method":[
            
         ],
         "name":"dataset1testdata",
         "time_created":"2021-08-12T19:15:09",
         "authors":[
            "admin"
         ]
      },
      {
         "id":29671,
         "labels":[
            "Dataset"
         ],
         "global_entity_id":"55626ddc-bcb6-47d9-8095-68129d521d15-1628277976",
         "creator":"admin",
         "modality":[
            "anatomical approach"
         ],
         "code":"aug06datasetcodetest",
         "total_files":9,
         "project_geid":"73d1fda2-a443-423a-96e5-6f0871b7d7cc-1628532375",
         "description":"test 123",
         "source":"",
         "title":"SAMPLE-DATASET",
         "type":"GENERAL",
         "tags":[
            "tag1",
            "tag2"
         ],
         "license":"v1.4.1",
         "time_lastmodified":"2021-08-09T19:13:16",
         "size":107908,
         "collection_method":[
            "import"
         ],
         "name":"aug06datasetcodetest",
         "time_created":"2021-08-06T19:26:16",
         "authors":[
            "admin"
         ]
      }
   ]
}
    )


class DatasetDetailResponse(APIResponse):
    """
    Dataset list response class
    """
    result: dict = Field({}, example={
   "code":200,
   "error_msg":"",
   "result":{
      "general_info":{
         "id":31401,
         "labels":[
            "Dataset"
         ],
         "global_entity_id":"3834290c-90c6-4c21-8642-c1f79cf2a145-1628791125",
         "creator":"admin",
         "modality":[
            
         ],
         "code":"sampletestdataset",
         "project_geid":"6c62dc07-a0f4-4a58-9491-d4a46c2adc79-1628775520",
         "total_files":6,
         "description":"1",
         "source":"",
         "title":"SAMPLE-dataset",
         "type":"GENERAL",
         "tags":[
            
         ],
         "license":"",
         "time_lastmodified":"2021-08-12T18:30:55",
         "size":6291456,
         "collection_method":[
            
         ],
         "name":"sampletestdataset",
         "time_created":"2021-08-12T17:58:45",
         "authors":[
            "admin"
         ]
      },
      "version_detail":[
         {
            "dataset_code":"sampletestdataset",
            "dataset_geid":"3834290c-90c6-4c21-8642-c1f79cf2a145-1628791125",
            "version":"1.0",
            "created_by":"admin",
            "created_at":"2021-08-12 18:15:54.115753",
            "location":"minio://http://10.3.7.220/testdataredcap2/versions/testdataredcap2_2021-08-12 14:15:53.608877.zip",
            "notes":"1"
         }
      ],
      "version_no":1
   }
})
