---
name: opencode
description: Delega una tarea sencilla y mecánica a OpenCode (agente de consola con modelos baratos o gratis, p. ej. DeepSeek) para ahorrar tokens de Claude. Úsala para borradores, scripts pequeños, renombrar o reformatear archivos, resúmenes o traducciones, nunca para decisiones de diseño, lore, revisiones finales ni nada que borre o publique.
---

# Delegar en OpenCode

OpenCode es otro agente de consola instalado en este PC. Usa modelos más baratos que Claude.
Tú sigues siendo el responsable: le das la tarea, revisas lo que hace y decides si vale.

## Antes de usarla
1. Comprueba que existe: `opencode --version`. Si no está, díselo a Antonio y para.
2. Mira qué modelos tiene: `opencode models`. Prefiere uno de DeepSeek o uno marcado como gratis.
   No leas ni enseñes claves de API.

## Cómo pasarle una tarea
Ejecútalo sin modo interactivo, dentro de una carpeta de trabajo aislada:

```
opencode run -m <proveedor/modelo> "<tarea completa y autocontenida>"
```

- La tarea tiene que llevar todo lo que necesita: qué hacer, qué archivos, cómo debe quedar el resultado.
- Ponle límites claros: «no borres nada», «solo escribe en esta carpeta».
- Si la orden no termina en unos minutos, párala y cuéntalo.

## Cuándo sí
Borradores de texto, scripts pequeños, convertir formatos, renombrar en lote, resumir documentos largos, primeras versiones que luego revisas tú.

## Cuándo no
Lore y nombres definitivos, dirección artística, el juez de criaturas, decisiones legales o de menores, cualquier cosa que borre, publique, haga push o maneje datos personales (DeepSeek envía los datos a servidores en China).

## Después
1. Revisa siempre el resultado (léelo o ejecútalo). No lo des por bueno sin mirarlo.
2. Cuéntale a Antonio en pocas líneas: qué modelo usaste, cuánto tardó, si salió bien a la primera y qué tuviste que corregir.
