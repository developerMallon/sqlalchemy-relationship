from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, ForeignKey, String, Integer
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional


# Configuração do SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarando a base
Base = declarative_base()


# ============= DEFINIÇÃO DOS MODELOS ==============
class Usuario(Base):
    __tablename__ = 'usuario'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    senha = Column(String)

    produtos = relationship('Produto', back_populates='usuario')


class Produto(Base):
    __tablename__ = 'produto'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    usuario_id = Column(Integer, ForeignKey('usuario.id', name='fk_usuario'))

    usuario = relationship('Usuario', back_populates='produtos')


# ============= DEFINIÇÃO DOS SCHEMAS ==============
class ProdutoSchema(BaseModel):
    id: Optional[int]
    nome: str
    usuario_id: int
    # usuario: Optional[UsuarioSchema]

    class Config:
        orm_mode = True
        
class UsuarioSchema(BaseModel):
    id: Optional[int]
    nome: str
    senha: str
    produtos: List[ProdutoSchema]

    class Config:
        orm_mode = True





# ============ App FastAPI ===========
app = FastAPI()

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======== ROTAS PARA USUÁRIOS ===========
@app.post('/usuario')
def adicionar_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):

    db_usuario = Usuario(nome=usuario.nome, senha=usuario.senha)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@app.get('/usuario', response_model=List[UsuarioSchema])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios


@app.put('/usuario/{id}')
def editar_usuario(id: int, nome: str, senha: str, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == id).first()

    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db_usuario.nome = nome
    db_usuario.senha = senha
    db.commit()
    db.refresh(db_usuario)

    return db_usuario

@app.delete('/usuario/{id}')
def excluir_usuario(id: int, db: Session = Depends(get_db)):

    db_usuario = db.query(Usuario).filter(Usuario.id == id).first()

    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_usuario)
    db.commit()
 
    return {
            "success": True,
            "message": f"Usuário id: {id} excluído com sucesso"
    }


# ======== ROTAS PARA PRODUTOS ===========
@app.post('/produto')
def adicionar_produto(produto: ProdutoSchema, db: Session = Depends(get_db)):

    db_produto = Produto(nome=produto.nome, usuario_id=produto.usuario_id)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)

    return db_produto



@app.get('/produto', response_model=List[ProdutoSchema])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()



@app.put('/produto/{id}')
def editar_produto(id: int, usuario_id: int, nome: str, db: Session = Depends(get_db)):
    db_produto = db.query(Produto).filter(Produto.id == id).first()

    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db_produto.nome = nome
    db_produto.usuario_id = usuario_id
    db.commit()
    db.refresh(db_produto)

    return db_produto



@app.delete('/produto/{id}')
def excluir_produto(id: int, db: Session = Depends(get_db)):

    db_produto = db.query(Produto).filter(Produto.id == id).first()

    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(db_produto)
    db.commit()
 
    return {
            "success": True,
            "message": f"Produto id: {id} excluído com sucesso"
    }
