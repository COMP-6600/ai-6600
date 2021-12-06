# Deep Learning Watermark Removal

A web service for automating a watermark removal process using deep learning. 
Simply upload an image in a square aspect ratio and the output will be displayed alongside it.

## Setup
This page acts as a monorepo, uniting the frontend and backend into a single repository. That said, it requires multiple build and setup processes.
There are two virtual environments for this program, one is for the frontend and one is for the backend.

### Frontend
- Ensure that node >=17.1.0 and npm >=8.1.3 are installed on the target system.
- While on the root directory, run ```npm install```. Appropriate mappings have been provided so the project can be ran and built without having to ```cd frontend``` before installing dependencies, for convenience.
- To build the project for static serving using the backend, run ```npm run build```

### Backend
- This project relies on [poetry](https://python-poetry.org/) for virtual environment generation, but a requirements.txt file was also provided for convenience and can be loaded using ```pipenv```, ```virtualenv``` or simply using ```pip install -r requirements.txt``` if you'd like to avoid using an isolated environment. (not recommended)
- To install using poetry, run ```poetry install```
- To run the backend, ensure the appropriate environment variables have been loaded for it and the frontend has been built, then ```cd backend``` and ```poetry run python -m main.py```
- The application should be served on localhost port 5000

### AI Model Training
- Trains and utilizes a deep learning model for removing watermarks from watermarked images.
- Uses Generative Adversarial Networks with an auto-encoder model.
- Images are cropped to 300x300 for memory limitations.

### Instructions for Training
- Either edit data location in code, or,
- Place data in dataset2/train/watermark for watermarked images, dataset2/train/no-watermark for non-watermarked images.
- Use provided .ipnyb to train the model.


- For Input/Output, place images into the IO folder, into the Input for input images.
- Run remover.py

### Requirements
- Python3.x
- tensorflow
- keras
- opencv2
- pandas
- numpy
- matplotlib
- sklearn
- pillow

### Dataset
- Datased used: https://www.kaggle.com/felicepollano/watermarked-not-watermarked-images
