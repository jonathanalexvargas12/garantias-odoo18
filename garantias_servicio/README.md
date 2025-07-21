# Módulo de Garantías y Servicio Técnico para Odoo 18

Este módulo extiende Odoo 18 para la gestión profesional de equipos de servicio técnico y presupuestos asociados, incluyendo lógica de negocio personalizada, validaciones y documentación profesional.

## Características principales

- **Gestión de Equipos de Servicio Técnico**
  - Registro de equipos con referencia única generada automáticamente.
  - Asociación de productos, clientes y fechas de ingreso/entrega.
  - Cálculo automático de garantía (90 días por defecto).
  - Acciones de estado: reparación, baja, entrega, borrador.
  - Relación directa con presupuestos generados.

- **Presupuestos de Servicio Técnico**
  - Registro de presupuestos vinculados a equipos y clientes.
  - Validación automática de cédula del propietario (solo números).
  - Asignación automática de cliente según equipo seleccionado.
  - Cálculo automático de totales y subtotales.
  - Acciones de estado: confirmar, realizado, cancelar, volver a borrador.

- **Líneas de Presupuesto**
  - Asociación de productos/servicios, cantidades y precios.
  - Actualización automática de descripción según producto.
  - Cálculo automático de subtotal por línea.

- **Vistas y Menús**
  - Vistas de lista, formulario y búsqueda para equipos y presupuestos.
  - Menús organizados para acceso rápido a equipos y presupuestos.
  - Indicadores visuales de garantía y estado.

- **Seguridad y Permisos**
  - Permisos detallados para usuarios sobre equipos, presupuestos y líneas.
  - Documentación profesional en todos los archivos de seguridad.

## Estructura de Archivos

- `models/technical_service.py`: Modelo de equipos de servicio técnico y lógica de negocio.
- `models/service_estimate.py`: Modelo de presupuestos y líneas, validaciones y acciones.
- `views/technical_service_views.xml`: Vistas y menús para equipos.
- `views/service_estimate_views.xml`: Vistas y menús para presupuestos.
- `security/ir.model.access.csv`: Permisos de acceso documentados.
- `__manifest__.py`: Metadatos y configuración del módulo.

## Instalación

1. Copia la carpeta `garantias_servicio` en el directorio `custom-addons` de tu instancia Odoo.
2. Instala las dependencias indicadas en `requirements.txt` si aplica.
3. Reinicia el servidor Odoo y actualiza la lista de módulos.
4. Instala el módulo desde la interfaz de Odoo.

## Uso

- Accede al menú "Servicio Técnico" para gestionar equipos y presupuestos.
- Crea equipos, registra ingresos y entregas, y genera presupuestos asociados.
- Utiliza las acciones de estado y los indicadores visuales para el seguimiento.

## Documentación y Mantenimiento

Todos los archivos del módulo están documentados profesionalmente con comentarios explicativos para facilitar el mantenimiento y la extensión futura.

## Autor y Licencia

- Autor: [Tu nombre o empresa]
- Licencia: [Especificar licencia, por ejemplo LGPL, MIT, etc.]

---

Para dudas, soporte o mejoras, contacta al responsable del módulo o consulta la documentación interna en cada archivo.
