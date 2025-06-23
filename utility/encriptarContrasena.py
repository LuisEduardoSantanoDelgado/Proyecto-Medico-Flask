from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def encriptar_contrasena(password_plano):
   
    hash_utf8 = bcrypt.generate_password_hash(password_plano).decode('utf-8')
    
    hash_bytes = hash_utf8.encode('utf-8')
    
    return hash_bytes

def verificar_contrasena(password, hash_contrasena):
    if isinstance(hash_contrasena, bytes):
        hash_contrasena = hash_contrasena.decode('utf-8')
    
    return bcrypt.check_password_hash(hash_contrasena, password)

    