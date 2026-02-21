# CookedChickenNuggets-HackEd2026

To make it work you have to open 2 terminals at the same time.

Terminal 1 (backend):

cd backend

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload --port 8000


Terminal 2 (Frontend):

cd UI/cooked-app

npm install

npm run dev


##Note: In backend/.env file, generate your own gemini api key and use it, since the project is still local so you'll need your local key to make it work. this will not be a problem once we deply the project.
