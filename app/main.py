from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import projects, testcases, users, testruns, statuses, auth, testresults
from app.db.database import init_db

init_db()

app = FastAPI(
    title="TMS API",
    version="1.0.0",
    description="Test Management System API"
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(users.user_router)
app.include_router(projects.router)
app.include_router(testcases.router)
app.include_router(testcases.project_router)
app.include_router(testruns.router)
app.include_router(testruns.project_router)
app.include_router(testresults.router)
app.include_router(testresults.project_router)
app.include_router(statuses.router)

@app.get("/")
def home():
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={})

@app.get("/projects")
def projects_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={})

@app.get("/projects/{project_id}")
def project_detail_page(request: Request, project_id: int):
    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={"project_id": project_id})

@app.get("/projects/{project_id}/testcases")
def project_detail_page(request: Request, project_id: int):
    return templates.TemplateResponse(
        request=request,
        name="testcases.html",
        context={"project_id": project_id})

# Страница со списком прогонов (отдельная страница)
@app.get("/projects/{project_id}/testruns")
def testruns_page(request: Request, project_id: int):
    """Страница управления прогонами тестов проекта"""
    return templates.TemplateResponse(
        request=request,
        name="testruns.html",
        context={"project_id": project_id}
    )


@app.get("/testruns/{testrun_id}")
def testrun_detail_page(request: Request, testrun_id: int):
    """Страница с результатами конкретного прогона"""
    return templates.TemplateResponse(
        request=request,
        name="testrun_detail.html",
        context={"testrun_id": int(testrun_id)}
    )

@app.get("/statuses")
def statuses_page(request: Request):
    """Страница управления статусами тестов"""
    return templates.TemplateResponse(
          request=request,
        name="statuses.html",
        context={}
    )


@app.get("/users")
def users_page(request: Request):
    """Страница управления пользователями"""
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={}
    )