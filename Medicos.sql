-- ES PARA SQL SERVER
CREATE DATABASE Medicos;
USE Medicos;

CREATE TABLE RolesMedicos(
	ID_rol INT IDENTITY(1, 1) PRIMARY KEY,
	Nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Medicos(
	ID_medico INT IDENTITY(1, 1) PRIMARY KEY,
	Nombres NVARCHAR(100) NOT NULL,
	Apellido_paterno NVARCHAR(50) NOT NULL,
	Apellido_materno NVARCHAR(50),
	Cedula_profesional VARCHAR(20) NOT NULL,
	RFC CHAR(13) NOT NULL,
	Correo_electronico VARCHAR(254) NOT NULL,
	Contrasena VARBINARY(200) NOT NULL,
	Estatus BIT DEFAULT 1,
	ID_rol INT NOT NULL,
	FOREIGN KEY(ID_rol) REFERENCES RolesMedicos(ID_rol),
);

CREATE TABLE Pacientes(
	ID_paciente INT IDENTITY(1, 1) PRIMARY KEY,
	Nombres NVARCHAR(100) NOT NULL,
	Apellido_paterno NVARCHAR(50) NOT NULL,
	Apellido_materno NVARCHAR(50),
	Fecha_nacimiento DATE NOT NULL,
	Alergias VARCHAR(1000),
	Enfermedades_cronicas VARCHAR(1000),
	Antecedentes_familiares VARCHAR(1000),
	Estatus BIT DEFAULT 1,
    Edad INT NOT NULL,
);

CREATE TABLE Citas(
	ID_cita INT IDENTITY(1, 1) PRIMARY KEY,
	Peso_paciente DECIMAL(5, 2) NOT NULL CHECK(Peso_paciente > 0 AND Peso_paciente <= 400),
	Altura_paciente DECIMAL(5, 2) NOT NULL CHECK(Altura_paciente > 0 AND Altura_paciente <= 250),
	Temperatura_paciente DECIMAL(4, 2) NOT NULL CHECK(Temperatura_paciente > 0 AND Temperatura_paciente <= 100),
	LPM_paciente SMALLINT NOT NULL,
	SDO_paciente SMALLINT NOT NULL,
	Glucosa_paciente SMALLINT NOT NULL,
	Estatus BIT DEFAULT 1,
	ID_paciente INT NOT NULL,
	ID_medico INT NOT NULL,
	FOREIGN KEY(ID_paciente) REFERENCES Pacientes(ID_paciente),
	FOREIGN KEY(ID_medico) REFERENCES Medicos(ID_medico)
);

CREATE TABLE Diagnosticos(
	ID_diagnostico INT IDENTITY(1, 1) PRIMARY KEY,
	Sintomas_paciente NVARCHAR(MAX) NOT NULL,
	Diagnostico_paciente NVARCHAR(MAX) NOT NULL,
	Tratamiento_paciente NVARCHAR(MAX) NOT NULL,
	URL_estudios_paciente VARCHAR(512),
	Estatus BIT DEFAULT 1,
);
CREATE TABLE Atiende(
    ID INT IDENTITY(1,1) PRIMARY KEY,
    ID_paciente INT NOT NULL,
    ID_medico INT NOT NULL,
	FOREIGN KEY(ID_paciente) REFERENCES Pacientes(ID_paciente),
	FOREIGN KEY(ID_medico) REFERENCES Medicos(ID_medico)
);

-- Insert de los roles medicos
INSERT INTO RolesMedicos(Nombre) VALUES
('Médico'),
('Médico administrador');
--CREACION DE ROLES 

CREATE ROLE Medico;


CREATE ROLE MedicoAdministrador;
-- Creacion de usuarios

CREATE USER UsuarioMedico FOR LOGIN MedicoLogin;

EXEC sp_addrolemember 'Medico', 'UsuarioMedico';

CREATE USER UsuarioMedicoAdministrador FOR LOGIN MedicoAdministradorLogin;

EXEC sp_addrolemember 'MedicoAdministrador', 'UsuarioMedicoAdministrador';

-- Asisgnación de permisos

GRANT SELECT, INSERT, UPDATE, DELETE ON Diagnosticos TO Medico;
GRANT SELECT, INSERT, UPDATE, DELETE ON Citas TO Medico;
GRANT SELECT, INSERT, UPDATE, DELETE ON Pacientes TO Medico;

GRANT SELECT, INSERT, UPDATE, DELETE ON RolesMedicos TO MedicoAdministrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON Medicos TO MedicoAdministrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON Diagnosticos TO MedicoAdministrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON Citas TO MedicoAdministrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON Pacientes TO MedicoAdministrador;


-- TABLAS DE AUDITORIA

-- Tabla de auditoría para RolesMedicos
CREATE TABLE Auditoria_RolesMedicos (
    ID_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    Tipo_modificacion VARCHAR(10) NOT NULL,  
    Fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    Usuario_modificacion NVARCHAR(100) NOT NULL,
    ID_rol INT NOT NULL
);

-- Tabla de auditoría para Medicos
CREATE TABLE Auditoria_Medicos (
    ID_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    Tipo_modificacion VARCHAR(10) NOT NULL,  
    Fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    Usuario_modificacion NVARCHAR(100) NOT NULL,
    ID_medico INT NOT NULL
);

-- Tabla de auditoría para Pacientes
CREATE TABLE Auditoria_Pacientes (
    ID_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    Tipo_modificacion VARCHAR(10) NOT NULL,  
    Fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    Usuario_modificacion NVARCHAR(100) NOT NULL,
    ID_paciente INT NOT NULL
);

-- Tabla de auditoría para Citas
CREATE TABLE Auditoria_Citas (
    ID_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    Tipo_modificacion VARCHAR(10) NOT NULL,  
    Fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    Usuario_modificacion NVARCHAR(100) NOT NULL,
    ID_cita INT NOT NULL
);

-- Tabla de auditoría para Diagnosticos
CREATE TABLE Auditoria_Diagnosticos (
    ID_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    Tipo_modificacion VARCHAR(10) NOT NULL, 
    Fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    Usuario_modificacion NVARCHAR(100) NOT NULL,
    ID_diagnostico INT NOT NULL
);

-- TRIGGERS DE ELIMINACION

-- Trigger para RolesMedicos
GO
CREATE TRIGGER trg_antiEliminacion_RolesMedicos
ON RolesMedicos
FOR DELETE
AS
BEGIN
    PRINT 'No se puede eliminar roles medicos';
    ROLLBACK;
END;

-- Trigger para Medicos
GO
CREATE TRIGGER trg_antiEliminacion_Medicos
ON Medicos
FOR DELETE
AS
BEGIN
    
    UPDATE Medicos
    SET Estatus = 0
    WHERE ID_medico IN (SELECT ID_medico FROM deleted);

    INSERT INTO Auditoria_Medicos (Tipo_modificacion, Usuario_modificacion, ID_medico)
    SELECT 'Delete', SYSTEM_USER, ID_medico FROM deleted;
    
    ROLLBACK;
END;

-- Trigger para Pacientes
GO
CREATE TRIGGER trg_antiEliminacion_Pacientes
ON Pacientes
FOR DELETE
AS
BEGIN
    
    UPDATE Pacientes
    SET Estatus = 0
    WHERE ID_paciente IN (SELECT ID_paciente FROM deleted);

    INSERT INTO Auditoria_Pacientes (Tipo_modificacion, Usuario_modificacion, ID_paciente)
    SELECT 'Delete', SYSTEM_USER, ID_paciente FROM deleted;
    
    ROLLBACK;
END;

-- Trigger para Citas
GO
CREATE TRIGGER trg_antiEliminacion_Citas
ON Citas
FOR DELETE
AS
BEGIN
  
    UPDATE Citas
    SET Estatus = 0
    WHERE ID_cita IN (SELECT ID_cita FROM deleted);

    INSERT INTO Auditoria_Citas (Tipo_modificacion, Usuario_modificacion, ID_cita)
    SELECT 'Delete', SYSTEM_USER, ID_cita FROM deleted;
    
    ROLLBACK;
END;

-- Trigger para Diagnosticos
GO
CREATE TRIGGER trg_antiEliminacion_Diagnosticos
ON Diagnosticos
FOR DELETE
AS
BEGIN
    
    UPDATE Diagnosticos
    SET Estatus = 0
    WHERE ID_diagnostico IN (SELECT ID_diagnostico FROM deleted);

    INSERT INTO Auditoria_Diagnosticos (Tipo_modificacion, Usuario_modificacion, ID_diagnostico)
    SELECT 'Delete', SYSTEM_USER, ID_diagnostico FROM deleted;

    ROLLBACK;
END;

-- AUDITORIAS PARA UPDATE E INSERT --------------

-- Trigger para insert y update en RolesMedicos
GO
CREATE TRIGGER trg_Auditoria_RolesMedicos
ON RolesMedicos
FOR INSERT, UPDATE
AS
BEGIN
    DECLARE @Tipo_modificacion VARCHAR(10);

    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'INSERT';
    END
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'UPDATE';
    END

    INSERT INTO Auditoria_RolesMedicos (Tipo_modificacion, Usuario_modificacion, ID_rol)
    SELECT @Tipo_modificacion, SYSTEM_USER, ID_rol
    FROM inserted;
END;

-- Trigger para insert y update en Medicos
GO
CREATE TRIGGER trg_Auditoria_Medicos
ON Medicos
FOR INSERT, UPDATE
AS
BEGIN
    DECLARE @Tipo_modificacion VARCHAR(10);

    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'INSERT';
    END
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'UPDATE';
    END

    INSERT INTO Auditoria_Medicos (Tipo_modificacion, Usuario_modificacion, ID_medico)
    SELECT @Tipo_modificacion, SYSTEM_USER, ID_medico
    FROM inserted;
END;

-- Trigger para insert y update en Pacientes
GO
CREATE TRIGGER trg_Auditoria_Pacientes
ON Pacientes
FOR INSERT, UPDATE
AS
BEGIN
    DECLARE @Tipo_modificacion VARCHAR(10);

    
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'INSERT';
    END
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'UPDATE';
    END

    INSERT INTO Auditoria_Pacientes (Tipo_modificacion, Usuario_modificacion, ID_paciente)
    SELECT @Tipo_modificacion, SYSTEM_USER, ID_paciente
    FROM inserted;
END;

-- Trigger para insert y update en Citas
GO
CREATE TRIGGER trg_Auditoria_Citas
ON Citas
FOR INSERT, UPDATE
AS
BEGIN
    DECLARE @Tipo_modificacion VARCHAR(10);

    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'INSERT';
    END
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'UPDATE';
    END

    INSERT INTO Auditoria_Citas (Tipo_modificacion, Usuario_modificacion, ID_cita)
    SELECT @Tipo_modificacion, SYSTEM_USER, ID_cita
    FROM inserted;
END;

-- Trigger para insert y update en Diagnosticos
GO
CREATE TRIGGER trg_Auditoria_Diagnosticos
ON Diagnosticos
FOR INSERT, UPDATE
AS
BEGIN
    DECLARE @Tipo_modificacion VARCHAR(10);

    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'INSERT';
    END
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        SET @Tipo_modificacion = 'UPDATE';
    END

    INSERT INTO Auditoria_Diagnosticos (Tipo_modificacion, Usuario_modificacion, ID_diagnostico)
    SELECT @Tipo_modificacion, SYSTEM_USER, ID_diagnostico
    FROM inserted;
END;

-- PROCEDIMIENTOS ALMACENADOS -----------------------
-- Login de Medicos
GO
CREATE PROCEDURE Obtener_Contrasena 
    @RFC CHAR(13)
AS
BEGIN
    DECLARE @Contrasena VARBINARY(200);

    IF EXISTS (SELECT 1 FROM Medicos WHERE RFC = @RFC)
    BEGIN
        
        SELECT @Contrasena = Contrasena
        FROM Medicos
        WHERE RFC = @RFC;

        SELECT @Contrasena AS Hash_Contrasena;
    END
    ELSE
    BEGIN
  
        SELECT 0 AS Hash_Contrasena;
    END
END;

-- Obtener ID_rol
GO
CREATE PROCEDURE Obtener_ID_Rol 
    @RFC CHAR(13)
AS
BEGIN
    DECLARE @ID_rol INT;

    IF EXISTS (SELECT 1 FROM Medicos WHERE RFC = @RFC)
    BEGIN
   
        SELECT @ID_rol = ID_rol
        FROM Medicos
        WHERE RFC = @RFC;

        SELECT @ID_rol AS ID_Rol;
    END
    ELSE
    BEGIN
      
        SELECT 0 AS ID_Rol;
    END
END;

-- AGREGAR MEDICO
GO
CREATE PROCEDURE InsertarMedico
    @Nombres NVARCHAR(100),
    @Apellido_paterno NVARCHAR(50),
    @Apellido_materno NVARCHAR(50),
    @Cedula_profesional VARCHAR(20),
    @RFC CHAR(13),
    @Correo_electronico VARCHAR(254),
    @Contrasena VARBINARY(200),
    @ID_rol INT,
    @Resultado INT OUTPUT  
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM Medicos WHERE RFC = @RFC)
    BEGIN
        SET @Resultado = 1;  
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM Medicos WHERE Correo_electronico = @Correo_electronico)
    BEGIN
        SET @Resultado = 2;  
        RETURN;
    END
    
    INSERT INTO Medicos (
        Nombres,
        Apellido_paterno,
        Apellido_materno,
        Cedula_profesional,
        RFC,
        Correo_electronico,
        Contrasena,
        ID_rol
    )
    VALUES (
        @Nombres,
        @Apellido_paterno,
        @Apellido_materno,
        @Cedula_profesional,
        @RFC,
        @Correo_electronico,
        @Contrasena,
        @ID_rol
    );

    SET @Resultado = 0;  
END;

-- EDITAR MEDICO
GO
CREATE PROCEDURE ActualizarMedico
    @ID_medico           INT,
    @Nombres             NVARCHAR(100),
    @Apellido_paterno    NVARCHAR(50),
    @Apellido_materno    NVARCHAR(50),
    @Cedula_profesional  VARCHAR(20),
    @RFC                 CHAR(13),
    @Correo_electronico  VARCHAR(254),
    @Contrasena          VARBINARY(200) = NULL,  
    @ID_rol              INT,
    @Resultado           INT OUTPUT              
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Medicos WHERE ID_medico = @ID_medico)
    BEGIN
        SET @Resultado = 1; 
        RETURN;
    END

    IF EXISTS (SELECT 1
               FROM Medicos
               WHERE RFC = @RFC
                 AND ID_medico <> @ID_medico)
    BEGIN
        SET @Resultado = 2;   -- 2 = RFC duplicado
        RETURN;
    END

    IF EXISTS (SELECT 1
               FROM Medicos
               WHERE Correo_electronico = @Correo_electronico
                 AND ID_medico <> @ID_medico)
    BEGIN
        SET @Resultado = 3;   -- 3 = correo duplicado
        RETURN;
    END

    UPDATE Medicos
    SET Nombres = @Nombres,
        Apellido_paterno = @Apellido_paterno,
        Apellido_materno = @Apellido_materno,
        Cedula_profesional = @Cedula_profesional,
        RFC = @RFC,
        Correo_electronico = @Correo_electronico,
        ID_rol = @ID_rol,
        Contrasena = @ContrasenA
    WHERE ID_medico = @ID_medico;

    SET @Resultado = 0;       
END

-- Eliminar medico

GO
CREATE PROCEDURE EliminarMedico
    @ID        INT,
    @Resultado  INT OUTPUT          
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Medicos WHERE ID_medico = @id)
    BEGIN
        SET @Resultado = 1;      -- 1 NO ENCONTRADO
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM Medicos WHERE ID_medico = @ID AND Estatus = 0)
    BEGIN
        SET @Resultado = 2;      -- 2 Ya estaba inactivo
        RETURN;
    END

    UPDATE Medicos
    SET Estatus = 0
    WHERE ID_medico = @ID;

    SET @Resultado = 0;          -- 0 ELIMINADO
END

-- Obtener tabla de pacientes
GO
CREATE PROCEDURE obtenerPacientes
    @ID_medico INT
AS
BEGIN
    SELECT DISTINCT 
        p.ID_paciente,
        p.Nombres,
        p.Apellido_paterno,
        p.Apellido_materno,
        CONVERT(VARCHAR(10), p.Fecha_nacimiento, 103) AS Fecha_nacimiento, -- Se formatea la fecha
        p.Alergias,
        p.Enfermedades_cronicas,
        p.Antecedentes_familiares,
        p.Estatus
    FROM Pacientes p
    INNER JOIN Atiende a ON p.ID_paciente = a.ID_paciente
    WHERE p.Estatus = 1 AND a.ID_medico = @ID_medico
END;

-- insertar paciente
GO
CREATE PROCEDURE InsertarPaciente
    @Nombres                 NVARCHAR(100),
    @Apellido_paterno        NVARCHAR(50),
    @Apellido_materno        NVARCHAR(50),
    @Fecha_nacimiento        VARCHAR(10),       
    @Alergias                VARCHAR(1000)  = NULL,
    @Enfermedades_cronicas   VARCHAR(1000)  = NULL,
    @Antecedentes_familiares VARCHAR(1000)  = NULL,
    @Resultado               INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @FechaNacDate DATE = TRY_CONVERT(DATE, @Fecha_nacimiento, 120); -- 120 = ISO 8601

    IF @FechaNacDate IS NULL
    BEGIN
        SET @Resultado = -2;                 -- fecha inválida
        RETURN;
    END
 
    IF EXISTS (SELECT 1
               FROM   Pacientes
               WHERE  Nombres          = @Nombres
                 AND  Apellido_paterno = @Apellido_paterno
                 AND  Apellido_materno = @Apellido_materno
                 AND  Fecha_nacimiento = @FechaNacDate)
    BEGIN
        SET @Resultado = 1;                 -- paciente ya existe
        RETURN;
    END

    DECLARE @Edad INT = dbo.edadPaciente(@FechaNacDate);

    INSERT INTO Pacientes (
        Nombres, Apellido_paterno, Apellido_materno,
        Fecha_nacimiento, Alergias, Enfermedades_cronicas,
        Antecedentes_familiares, Edad
    )
    VALUES (
        @Nombres, @Apellido_paterno, @Apellido_materno,
        @FechaNacDate, @Alergias, @Enfermedades_cronicas,
        @Antecedentes_familiares, @Edad
    );


    SET @Resultado = 0;                     -- éxito
END;


--Actualizar paciente
GO
CREATE PROCEDURE ActualizarPaciente
    @ID INT,
    @Nombres NVARCHAR(100),
    @Apellido_paterno NVARCHAR(50),
    @Apellido_materno NVARCHAR(50),
    @Fecha_nacimiento VARCHAR(10),  
    @Alergias VARCHAR(1000) = NULL,
    @Enfermedades_cronicas VARCHAR(1000) = NULL,
    @Antecedentes_familiares VARCHAR(1000) = NULL,
    @Resultado INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @FechaNacDate DATE = TRY_CONVERT(DATE, @Fecha_nacimiento, 120);  -- ISO 8601

    IF @FechaNacDate IS NULL
    BEGIN
        SET @Resultado = -2;  -- Fecha inválida
        RETURN;
    END

    IF NOT EXISTS (
        SELECT 1 FROM Pacientes WHERE ID_paciente = @ID
    )
    BEGIN
        SET @Resultado = 1;  -- Paciente no existe
        RETURN;
    END

    DECLARE @Edad INT = dbo.edadPaciente(@FechaNacDate);

    UPDATE Pacientes
    SET 
        Nombres = @Nombres,
        Apellido_paterno = @Apellido_paterno,
        Apellido_materno = @Apellido_materno,
        Fecha_nacimiento = @FechaNacDate,
        Alergias = @Alergias,
        Enfermedades_cronicas = @Enfermedades_cronicas,
        Antecedentes_familiares = @Antecedentes_familiares,
        Edad = @Edad
    WHERE ID_paciente = @ID;

    SET @Resultado = 0;  -- Actualización exitosa
END;

-- Eliminar Paciente
GO
CREATE PROCEDURE EliminarPaciente
    @ID         INT,
    @Resultado  INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    
    IF NOT EXISTS (
        SELECT 1 FROM Pacientes WHERE ID_paciente = @ID
    )
    BEGIN
        SET @Resultado = 1;  -- paciente no encontrado
        RETURN;
    END

    
    IF EXISTS (
        SELECT 1 FROM Pacientes WHERE ID_paciente = @ID AND Estatus = 0
    )
    BEGIN
        SET @Resultado = 2;  -- Ya estaba inactivo
        RETURN;
    END

    UPDATE Pacientes
    SET Estatus = 0
    WHERE ID_paciente = @ID;

    SET @Resultado = 0;  -- Eliminado correctamente
END;

-- FUNCIONES ---------------------
GO
CREATE FUNCTION dbo.NombreCompletoMedico (@rfc CHAR(13))
RETURNS NVARCHAR(200)
AS
BEGIN
    DECLARE @nombreCompleto NVARCHAR(200);

    SELECT @nombreCompleto = CONCAT(Nombres, ' ', Apellido_paterno, ' ', Apellido_materno)
    FROM Medicos
    WHERE RFC = @rfc;

    RETURN @nombreCompleto;
END

GO
CREATE FUNCTION dbo.IDMedico (@rfc CHAR(13))
RETURNS INT
AS
BEGIN
    DECLARE @IDMedico INT;
    SELECT @IDMedico = ID_medico FROM Medicos WHERE RFC = @rfc;
    RETURN @IDMedico;
END

go
CREATE FUNCTION dbo.DatosMedico (@rfc CHAR(13))
RETURNS TABLE
AS
RETURN (
    SELECT *
    FROM Medicos
    WHERE RFC = @rfc
);

-- asigna la edad de los pacientes
GO
CREATE FUNCTION dbo.edadPaciente (@FechaNacimiento DATE)
RETURNS INT
AS
BEGIN
    DECLARE @Hoy DATE = GETDATE();
    DECLARE @Edad INT;

    SET @Edad = DATEDIFF(YEAR, @FechaNacimiento, @Hoy);

    IF MONTH(@FechaNacimiento) > MONTH(@Hoy)
        OR (MONTH(@FechaNacimiento) = MONTH(@Hoy) AND DAY(@FechaNacimiento) > DAY(@Hoy))
        SET @Edad = @Edad - 1;

    RETURN @Edad;
END;

-- obtiene el id del paciente
GO
CREATE FUNCTION dbo.IDPaciente (
    @Nombres NVARCHAR(100),
    @Apellido_paterno NVARCHAR(50),
    @Apellido_materno NVARCHAR(50),
    @Fecha_nacimiento VARCHAR(10)
)
RETURNS INT
AS
BEGIN
    DECLARE @ID INT
    DECLARE @FechaNacDate DATE = TRY_CONVERT(DATE, @Fecha_nacimiento, 120)

    IF @FechaNacDate IS NULL
        RETURN NULL

    SELECT TOP 1 @ID = ID_paciente
    FROM Pacientes
    WHERE 
        Nombres = @Nombres AND
        Apellido_paterno = @Apellido_paterno AND
        Apellido_materno = @Apellido_materno AND
        Fecha_nacimiento = @FechaNacDate

    RETURN @ID
END;


