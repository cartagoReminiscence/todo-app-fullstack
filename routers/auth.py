import sys
sys.path.append('..')

from typing import Optional
from fastapi import status, Depends, HTTPException, APIRouter, Request, Form, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, JWTError

from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse

SECRET_KEY = "holaATodos!"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

templates = Jinja2Templates(directory='templates')

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_hash_password(password):
    return bcrypt_context.hash(password)

def verify_pasword(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username, password, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_pasword(password, user.hashed_password):
        return False
    return user

def create_access_token(username, user_id, expires_delta: Optional[timedelta] = None):
    encode = {'sub': username, 'id': user_id}
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(minutes=15)
    encode.update({'exp': expires})

    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={401:{'User':'Not authorized'}}
)

@router.post('/token')
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key='access_token', value=token, httponly=True)

    return True

async def get_current_user(request: Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        id = payload.get('id')
        if username is None or id is None:
            logout(request)
        return {'username': username, 'id': id}

    except JWTError:
        raise HTTPException(status_code=404, detail='Not found')

@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request})

@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = 'Nombre de usuario o contraseña incorrecto'
            return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
        return response

    except HTTPException:
        msg = 'Unknown error'
        return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

@router.get('/logout')
async def logout(request: Request):
    msg = 'Sesión terminada'
    response = templates.TemplateResponse('login.html', context={'request': request, 'msg': msg})
    response.delete_cookie(key='access_token')
    return response

@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse('register.html', context={'request': request})

@router.post('/register', response_class=HTMLResponse)
async def register_user(request: Request,
                        email: str = Form(...),
                        username: str = Form(...),
                        firstname: str = Form(...),
                        lastname: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(...),
                        db: Session = Depends(get_db)):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = 'Solicitud de registro inválida'
        return templates.TemplateResponse('register.html', context={'request': request, 'msg': msg})

    user_model = models.Users()
    user_model.email = email
    user_model.username = username
    user_model.first_name = firstname
    user_model.last_name = lastname

    hashed_password = get_hash_password(password)
    user_model.hashed_password = hashed_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = 'Usuario creado existosamente'
    return templates.TemplateResponse('login.html', context={'request': request, 'msg': msg})