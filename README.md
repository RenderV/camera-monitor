# camera-monitor

This project was made to practice flask. It is a footprint of another project that is currently in development with Django, PostgresSQL, and Next.js.

It's a camera monitoring system designed to be complemented with a object detection model. When a new detection is added to the database, the user is notified. It's possible to remove register and select an area of interest where the model will perform its detection.

Please note that this repository solely contains the user interface and routing logic.

#### Table of contents
  * [Images](#images)
  * [Usage](#usage)

## Images

![Screenshot from 2023-08-27 23-18-13](https://github.com/RenderV/camera-monitor/assets/92237089/31c19c60-82e1-45b6-94dd-57f273cfcf67)
![Screenshot from 2023-08-27 23-19-08](https://github.com/RenderV/camera-monitor/assets/92237089/614c0bb5-a8c3-416f-87d5-4f7593ea9e74)
![Screenshot from 2023-08-27 23-19-23](https://github.com/RenderV/camera-monitor/assets/92237089/ad9ca32e-518a-4115-a592-019f6b75b527)
![Screenshot from 2023-08-27 23-19-35](https://github.com/RenderV/camera-monitor/assets/92237089/c7e254e8-ea8c-4d6c-a026-03a87c58bd50)
![Screenshot from 2023-08-27 23-28-48](https://github.com/RenderV/camera-monitor/assets/92237089/e7bd90a3-53dd-4eae-9554-768966a42acc)
![Screenshot from 2023-08-27 23-31-37](https://github.com/RenderV/camera-monitor/assets/92237089/10804703-6aac-4ffa-8625-fa5312a99ade)


## Usage

To use the application, follow these instructions:
1. Install the project dependencies with `pip install -r requirements.txt`.
2. Install MongoDB and configure a local server with port `27107`, or change the `app.config.MONGODB_URL` variable in `app/__init__.py`.
3. (Optional) Implement your choice of computer vision model at `inferences/__init__.py`. Otherwise, a placeholder video will be used.

Each report can be added via the API or directly using the ORM.

Via ORM:
```py
def send_info(location, image, save_folder, extension='.jpg'):
    image_bytes = cv2.imencode(extension, image)[1].tobytes()
    file_hash = hashlib.md5(image_bytes).hexdigest()+str(random.randint(0, 1000000))
    file_path = os.path.join(save_folder, file_hash+extension)
    cv2.imwrite(file_path, image)
    report = Report(location=location, image_url=file_hash+extension)
    report.save()
```
In this case, the image path should be the same as `app.config.UPLOAD_FOLDER`

Via API:
```py
  def send_image_by_image_path(url, image_path, location, name=None):
      # Names should end with an extension for this function
      name = os.path.basename(image_path) if name is None else name
      files = {'file': (name, open(image_path, 'rb').read(), 'application/octet-stream')}
      data = {'location': location}
      r = requests.post(url, files=files, data=data)
      return r
```
