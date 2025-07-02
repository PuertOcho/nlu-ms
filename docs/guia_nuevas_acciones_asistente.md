# Guía detallada para **añadir nuevas acciones** al asistente Puerto Ocho  
*(control de PCs: “mundo virtual”, domótica: “mundo físico”)*

---

## Índice
1. Conceptos clave  
2. Flujo general de alta de una acción  
3. Ejemplo completo A → **“bloquear el PC”** (mundo virtual)  
4. Ejemplo completo B → **“poner la calefacción a 22 °C”** (mundo físico)  
5. Pruebas automatizadas  
6. Buenas prácticas & seguridad  

---

## 1 · Conceptos clave
| Término | Descripción |
|---------|-------------|
| **Intención (intent)** | Acción que el usuario desea realizar → `bloquear_pc`, `subir_calefaccion` … |
| **Entidad (entity)**   | Datos adicionales que la intención necesita → `temperatura=22` |
| **Dominio**           | Agrupador lógico de intenciones → `pc`, `hogar`, `oficina` |
| **NLU (nlu-ms)**      | Microservicio que entiende la frase (Rasa + TensorFlow GPU). |
| **Intent Manager**    | Microservicio Java que recibe la intención y ejecuta la **acción**. |
| **Clases de acción**  | `SystemTools`, `SmartHomeTools`, etc. (invocan comandos, APIs, MQTT…). |

---

## 2 · Flujo general de alta de una nueva acción

| Paso | Carpeta / Archivo | Descripción |
|------|-------------------|-------------|
| **A. Añadir ejemplos** | `nlu-ms/server/training_data/intents/<dominio>_<locale>.yml` | Crea bloque:<br>`- intent: bloquear_pc`<br>&nbsp;&nbsp;`examples: |`<br>&nbsp;&nbsp;`  - bloquea el pc`<br>&nbsp;&nbsp;`  - bloquea mi computadora` … |
| **B. (opcional) Entidades** | `training_data/entities/*.txt` | Añade listas o sinónimos si tu acción necesita datos específicos. |
| **C. Re-entrenar NLU** | API o script | `curl -X POST "http://localhost:5001/train?domain=pc&locale=es"` |
| **D. Mapear intención → acción** | `SmartAssistantService.java` | Añade `case BLOQUEAR_PC -> { ... }` que invoque `SystemTools.lockComputer()`. |
| **E. Implementar acción** | `SystemTools.java` | Código para ejecutar comando / llamar API. |
| **F. Registrar constante** | `Assistant.java` (o Enum) | `public static final String BLOQUEAR_PC = "bloquear_pc";` |
| **G. Configuración externa** | `configms/.../*.yml` | Tokens, IPs, topics, etc. |

---

## 3 · Ejemplo A – “bloquear el PC” (mundo virtual)

### 3.1 Entrenamiento
```yaml
# pc_es.yml
- intent: bloquear_pc
  examples: |
    - bloquea el pc
    - bloquea mi computadora
    - bloquear pantalla
    - bloquea el equipo
    - bloquea el ordenador
```
```bash
curl -X POST "http://localhost:5001/train?domain=pc&locale=es"