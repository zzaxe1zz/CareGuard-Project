# Suite de Pruebas Automatizadas y Cobertura (`pytest` & `pytest-cov`)

Este documento detalla la configuración, estructura, ejecución, métricas de cobertura de código y enlaces a la documentación oficial para la suite de pruebas automatizadas del proyecto **CareGuard**.

## Hojas de Cálculo Oficiales del Proyecto

La trazabilidad, diseño de casos de prueba y reportes ejecutivos de calidad se gestionan en los siguientes documentos oficiales:

* **Reporte de Casos de Prueba (Matriz y Detalle):**

  [test-case-report-CareGuard](https://docs.google.com/spreadsheets/d/1AYbwzGhQeGoozZFYNNaS71DkFR0l1y1jUKbAZniopks/edit?usp=sharing)

  *Contiene la lista desglosada de los 61 sub-criterios de prueba (MT, IT, ST), asignaciones de testers, fechas de ejecución y estados actualizados.*

* **Reporte Resumen Ejecutivo de Software Testing (SWT):**

  [SWT_summary_report_Project_CareGuard](https://docs.google.com/spreadsheets/d/1h-IHiyEdX4iXiO8733SXxf7HdIcZs8rW-lQ9wloNnEg/edit?usp=sharing)

  *Contiene las métricas consolidadas del proyecto, gráficos circulares de estado de pruebas, porcentaje de defectos, trazabilidad por controlador/módulo y resumen de entrega (Milestone App Release).*

## Resumen Ejecutivo de Ejecución

* **Total de Casos de Prueba:** 61 casos independientes.

* **Resultado de Ejecución:** **61 PASSED** (100% de efectividad).

* **Tiempo de Ejecución:** \~0.52 segundos.

* **Cobertura Total del Código:** **89% TOTAL** (100% en capas de prueba).

## Requisitos e Instalación

Para ejecutar la suite de pruebas y generar los reportes de cobertura, es necesario contar con Python 3.x y las herramientas `pytest` y `pytest-cov`.

```
# Instalación del plugin de cobertura
pip install pytest-cov

```

## Comandos de Ejecución

### 1. Ejecución completa de la suite de pruebas

```
pytest -v

```

### 2. Ejecución con Reporte de Cobertura en Consola

```
pytest --cov

```

### 3. Reporte de Cobertura Detallado (Mostrando líneas no cubiertas)

```
pytest --cov=. --cov-report=term-missing

```

### 4. Generar Reporte de Cobertura en Formato HTML

```
pytest --cov=. --cov-report=html

```

*(El reporte se creará en la carpeta `htmlcov/index.html`).*

## Estructura de la Suite de Pruebas

La suite de pruebas está estructurada en tres niveles metodológicos:

```
tests/
├── MT/    # Pruebas Modulares (Unit Testing - Caja Blanca)
│   ├── test_mt_01_descansos.py             (4 tests)
│   ├── test_mt_02_kiosco_reset.py          (4 tests)
│   ├── test_mt_03_alta_usuarios.py         (5 tests)
│   ├── test_mt_04_motor_sobrecarga.py      (5 tests)
│   └── test_mt_05_alerta_inmutabilidad.py  (4 tests)
├── IT/    # Pruebas de Integración (Integration Testing - Caja Gris)
│   ├── test_it_01_estado_animo.py          (4 tests)
│   ├── test_it_02_apoyo_psicologia.py      (4 tests)
│   ├── test_it_03_alerta_bandeja.py        (3 tests)
│   ├── test_it_04_estados_alerta.py        (4 tests)
│   └── test_it_05_evaluacion_kiosco.py     (5 tests)
└── ST/    # Pruebas de Sistema (System Testing - Caja Negra / E2E)
    ├── test_st_01_historial_restringido.py  (3 tests)
    ├── test_st_02_expediente_confidencial.py (3 tests)
    ├── test_st_03_rendimiento_gui.py       (3 tests)
    ├── test_st_04_dashboard_admin.py       (5 tests)
    └── test_st_05_rbac_seguridad.py        (5 tests)

```

## Reporte Oficial de Cobertura de Código

| Módulo / Archivo | Declaraciones (Stmts) | Errores (Miss) | Cobertura (Cover) | 
| ----- | ----- | ----- | ----- | 
| `database/audit_logger.py` | 18 | 12 | 33% | 
| `database/db_adapter.py` | 35 | 25 | 29% | 
| `tests/IT/*` (5 archivos) | 173 | 0 | **100%** | 
| `tests/MT/*` (5 archivos) | 125 | 3 | **98%** *(Promedio)* | 
| `tests/ST/*` (5 archivos) | 133 | 0 | **100%** | 
| `tests/conftest.py` | 27 | 5 | 81% | 
| `utils/reset_timer.py` | 27 | 13 | 52% | 
| **TOTAL** | **538** | **58** | **89%** | 

## Trazabilidad de Requisitos Cubiertos

1. **MT-01 a MT-05:** Validación determinista de tiempos de descansos, reset del kiosco (30s), PBKDF2 Hashing en contraseñas, umbral de sobrecarga laboral (>12h extra o 3 días estrés) e inmutabilidad de alertas.

2. **IT-01 a IT-05:** Persistencia real en base de datos SQLite con aislamiento por usuario, bandeja de entrada de Psicología, transiciones válidas del ciclo de vida de alertas (`PENDIENTE` $\rightarrow$ `EN_ATENCION` $\rightarrow$ `CERRADA`) y evaluaciones anónimas del kiosco.

3. **ST-01 a ST-05:** Seguridad RBAC (Control de Acceso Basado en Roles), visualización de historiales confidenciales, rendimiento del sistema en consultas de alta densidad ($\le 2.0\text{s}$) y dashboard anonimizado para Administradores.