import json
import unittest

from app.adopt_generation import adopt_generation


class TestAdoptFunction(unittest.TestCase):

    def test_assign_combination(self):
        test_input = json.loads('''{
            "area" : {
                "name" : "Berlin",
                "type" : "city"
            },
            "entities" : [
                {
                    "id" : 0,
                    "name" : "park"
                },
                {
                    "filters" : [
                        {
                            "name" : "distance",
                            "operator" : "<=",
                            "value" : "200m"
                        },
                        {
                            "name" : "type",
                            "operator" : "=",
                            "value" : "fountain"
                        }
                    ]
                }
            ],
            "relations" : [
                {
                    "name" : "dist",
                    "source" : 0,
                    "target" : 1,
                    "value" : "200m"
                }
            ]
        }''')

        expected_output = json.loads('''{
   "area":{
      "type":"area",
      "value":"Berlin"
   },
   "nodes":[
      {
         "id":0,
         "type":"nwr",
         "filters":[
            {
               "or":[
                  {
                     "key":"landuse",
                     "operator":"=",
                     "value":"recreation_ground"
                  },
                  {
                     "key":"landuse",
                     "operator":"=",
                     "value":"village_green"
                  },
                  {
                     "key":"leisure",
                     "operator":"=",
                     "value":"park"
                  },
                  {
                     "key":"leisure",
                     "operator":"=",
                     "value":"garden"
                  }
               ]
            }
         ],
         "name":"park",
         "display_name":"parks"
      }
   ],
   "edges":[
      {
         "type":"dist",
         "source":0,
         "target":1,
         "distance":"200m"
      }
   ]
}''')

        predicted_output = adopt_generation(test_input)
        assert predicted_output == expected_output


if __name__ == '__main__':
    unittest.main()
