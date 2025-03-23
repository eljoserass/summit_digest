# Plan for submission
build an app that userrs can register and login on. once logged in, users will see summaries request, and an option to create one. to create a summary, users will upload the .zip of the files they want to get insights for, this will trigger a process where a llm will read through each file extracting the main takeway from that file. once all the files has been processed individually, a long context model will read all the documents at once, plus the extracted takeway to create a comprehensive report of the summit. user will be able to watch as the model is going through each file to track process, and see the resulting summary.
## Steps for submission
### API
  - set up database
  - set up llm api
  - resgister and login endpoints
  - POST digest with a .zip upload
  - GET digest by id
  - GET user digests
  - unzip file and store them in /user/request folder, store file name in digest
  - GET media from .zip by path (Auth)
  - run process that goes through all files, get insight form llm, store it in db. at the end call process that opens all files, and pass them to llm to get full summary, store it in db
  - unit tests for register and login
  - unit test for digest create and display
  - unit test for user digests

### FRONTEND
  - login page
  - register page
  - show digests of user with "processing" or tile, N files, time of creation
  - show digest by ID, "processing" or tile, time of creation, list of files with the "processing" or insight. show summary result in rendered markdown when available
  - create simple landing page if enough time

## Stack
- Backend and Frontend: FastAPI + Jinja Templating
- Database: MySQL / SQLite
- Models: OpenAI, potentially using gemini-2-flash for long context
