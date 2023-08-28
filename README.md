# camera-monitor

This project was made to practice flask. It is a footprint of another project that is currently in development with Django, PostgresSQL, and Next.js.

#### Table of contents
  * [Images](#images)
  * [Usage](#usage)

## Images

![image](https://github.com/RenderV/camera-monitor/assets/92237089/f8c9a9c2-333c-4faf-a4f3-d66f67e7e325)
![image](https://github.com/RenderV/camera-monitor/assets/92237089/7cb6b8d2-a6ee-4a07-bada-601a12b4c9a3)
![image](https://github.com/RenderV/camera-monitor/assets/92237089/c0f5a222-5635-4ef7-b195-8b985fd0e97f)
![image](https://github.com/RenderV/camera-monitor/assets/92237089/4c3bb30b-922a-4f17-bffb-77da335326a8)
![image](https://github.com/RenderV/camera-monitor/assets/92237089/eae47bac-762c-4935-a44d-18c7b70c79ac)
![image](https://github.com/RenderV/camera-monitor/assets/92237089/e45fe47d-464c-4adb-9522-d89885526a8b)


## Usage

This repository only contains the user interface and backend logic.

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
