from predict import predict_attributes

result = predict_attributes(
    "test_images/person.jpg"
)

from pprint import pprint

pprint(result)