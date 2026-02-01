# 🔍 DIAGNÓSTICO DE PROBLEMAS - Streamlit Session

## Fecha: 2026-01-30 22:30

---

## ❌ Problema 1: "Hamburguesa" → Profile (Incorrecto)

### Input del Usuario:
```
"Acabo de comprar una hamburguesa de camino a casa, apunta eso como mi cena"
```

### Detección Actual:
```
⚡ [ROUTER] Intención: 'profile'
🚀 [Background] Guardando en Qdrant (detectado: profile)...
```

### ¿Por qué pasó?

**Función `_should_save_to_longterm()`** detectó patrón permanente:
```python
r"(me gusta|odio|me encanta|detesto|amo)"  # NO matchea
# PERO...
```

El problema es que Mem0 extrae: **"Compró una hamburguesa para cenar"**

**Causa raíz:** Router debió clasificar como **chat** o **finance**, no profile.

**Utterances de finance:**
```python
"compre unas zapatillas",  # ✅ Coincide
"compre pasajes",          # ✅ Coincide
# Pero "compré hamburguesa" es similar
```

**Debería detectarse como:** `finance` (tiene monto implícito + compra)

---

## ❌ Problema 2: Finance Extractor Falla con Contexto

### Inputs que Fallaron:

**Intento 1:**
```
👺 "fueron 5 soles que gaste alli"
🔍 No se encontraron items - retornando error
```

**Intento 2:**
```
👺 "gaste 5 soles en cenar hoy ok"
🔍 No se encontraron items - retornando error
```

### ¿Por qué falló?

El prompt del extractor es estricto:
```python
"""
REGLAS CRÍTICAS:
1. Solo extrae si hay un MONTO CLARO y un CONCEPTO.
```

**Análisis:**

| Input | Monto | Concepto | ¿Extrajo? |
|-------|-------|----------|-----------|
| "fueron 5 soles que gasté **allí**" | ✅ 5 soles | ❌ "allí" = referencia vaga | NO |
| "gasté 5 soles en **cenar**" | ✅ 5 soles | ✅ "cenar" | DEBERÍA ✅ |

**Problema:** El LLM 8B es demasiado estricto con "allí".

### Fix Implementado:

Agregado al prompt:
```python
"""
CONTEXTO CONVERSACIONAL:
- Si dice "allí", "eso", "esto" con un monto, ACEPTA como gasto válido.
- Merchant puede ser genérico: "compra", "gasto", "allí".
"""
```

---

## ❌ Problema 3: "Recuerdame llamar" → Chat (Incorrecto)

### Input:
```
👺 "cierto, recuerdame llamar a mama manana a las 10 am"
🗣️ [ROUTER] Conversación detectada (13.21ms) -> Directo a Mondri
```

### ¿Por qué falló?

**Router tasks utterances:**
```python
"recuerdame comprar leche",  # ✅
"recuerdame el cumpleaños",  # ✅
# ❌ "recuerdame llamar" NO está
```

**Semantic similarity:**
- "recuerdame llamar a mama" vs "recuerdame comprar leche"
- Similarity: ~0.45 (threshold: 0.50)
- Resultado: No matchea → va a chat

### Fix Implementado:

Agregados utterances específicos:
```python
"recuerdame llamar",
"tengo que llamar",
"avisar a mi mama",
"contactar al banco",
```

---

## 🎯 Fixes Aplicados

### Fix 1: Finance Extractor más Flexible

**Antes:**
```python
content: """
REGLAS CRÍTICAS:
1. Solo extrae si hay MONTO CLARO y CONCEPTO.
"""
```

**Ahora:**
```python
content: """
REGLAS CRÍTICAS:
1. Solo extrae si hay MONTO CLARO y CONCEPTO.

CONTEXTO CONVERSACIONAL:
- Si dice "allí", "eso", "esto" con monto → ACEPTA
- Merchant genérico OK: "compra", "gasto", "allí"
"""
```

### Fix 2: Tasks Router Mejorado

**Agregados 4 utterances:**
- "recuerdame llamar"
- "tengo que llamar"
- "avisar a mi mama"
- "contactar al banco"

---

## 🧪 Test de Regresión Recomendado

Prueba estos casos en Streamlit:

### Finance:
```
✅ "Gasté 25 soles en taxi"
✅ "fueron 5 soles que gasté allí"  ← Ahora debería funcionar
✅ "gaste 5 soles en cenar"
```

### Tasks:
```
✅ "Recuérdame llamar a mamá mañana"  ← Ahora debería funcionar
✅ "Tengo que llamar al banco"
```

### Profile:
```
✅ "Me llamo Roberto"
✅ "Me gusta el café"
❌ "Acabo de comprar hamburguesa"  ← Debería ir a chat/finance
```

---

## 💭 Sobre Daily.md en Finance/Tasks

### Tu Pregunta:
> "¿De qué le sirve daily.md si finance/tasks van a DB?"

### Mi Respuesta:

**SÍ tiene sentido por:**

1. **Contexto conversacional:**
```
Usuario: "Acabo de comprar una hamburguesa"
Usuario: "fueron 5 soles que gasté allí"  ← Necesita saber qué es "allí"
```

2. **Preguntas sobre acciones:**
```
Usuario: "¿Ya te dije que gasté en taxi?"
Usuario: "¿Qué tareas me pusiste?"
```

3. **Evitar duplicados:**
```
Usuario: "Gasté 20 soles en taxi"
Usuario: "fueron 20 soles" ← Detectar que ya lo dijo
```

### **Pero NO debería guardar:**
- ❌ Mensajes de confirmación: "[SYSTEM]: Gasto guardado" (ya arreglado)
- ❌ Solo el monto: "fueron 5 soles" (ya se guarda original)

### **Recomendación Final:**

**Mantener finance/tasks en daily.md** porque:
- Mejora el contexto conversacional
- Permite preguntas sobre historial reciente
- Costo mínimo (50KB/día)

**Si quieres optimizar:**
- Filtrar confirmaciones más agresivamente
- Limpiar daily.md después de síntesis nocturna

---

## 📋 Siguiente Paso

**Probar en Streamlit con los fixes:**

1. Reinicia Streamlit para cargar cambios
2. Prueba los 3 casos problemáticos
3. Verifica logs y DB

¿Quieres que ejecute tests automatizados para validar los fixes?
