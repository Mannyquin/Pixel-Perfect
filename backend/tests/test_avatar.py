from pprint import pprint

from predict import predict_attributes
from ai_generator import generate_avatar

IMAGE_PATH = "test_images/person.jpg"   # Change this to your test image

prediction = predict_attributes(IMAGE_PATH)

avatar = generate_avatar(
    prediction,
    style="ghibli",
)

print("\nPrediction")
pprint(prediction)

print("\nGenerated Prompt")
print(avatar.prompt.prompt)

print("\nDescriptors")
pprint(avatar.prompt.descriptors)

print("\nImage URL")
print(avatar.image_url)