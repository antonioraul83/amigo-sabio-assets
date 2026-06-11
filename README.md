# amigo-sabio-assets

Modelos públicos descargables por la app Amigo Sabio.

Solo contiene los binarios necesarios para que la app funcione. El código
fuente vive en otro repo (privado).

## Licencias

- `vector_estimator.onnx` y `vocoder.onnx`: SuperTonic TTS, Apache 2.0
  (Supertone Inc.).

## Releases

- `voice-models-v1`: 357 MB. Los 2 ONNX gordos del pipeline SuperTonic
  (text_encoder y duration_predictor van empaquetados directamente en
  el APK porque son ligeros).
