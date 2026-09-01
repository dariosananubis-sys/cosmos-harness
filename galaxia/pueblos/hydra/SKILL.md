---
cosmos: pueblo
nombre: hydra
padre: cientifico
resumen: Compone la configuracion del experimento y deja registrada la de cada corrida, sobreescribible desde la consola.
---

https://github.com/hydra-ecosystem/hydra - MIT - 10.626 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01). Nacio en Facebook Research; hoy lo mantiene la
comunidad en esta organizacion.

```bash
pip install hydra-core
```

```yaml
# conf/config.yaml
defaults:
  - modelo: lineal
semilla: 1234
datos:
  ruta: datos/limpio.parquet
  particion: 0.8
```

```python
# entrenar.py
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))     # la config de ESTA corrida, completa

if __name__ == "__main__":
    main()
```

```bash
python entrenar.py                                  # deja outputs/<fecha>/<hora>/.hydra/config.yaml
python entrenar.py semilla=7 modelo=arbol           # sobreescribe sin tocar el codigo
python entrenar.py -m semilla=1,2,3 datos.particion=0.7,0.8   # barrido cartesiano
```

Es la pieza que fija la ENTRADA del experimento. Complementa a `mlflow`, que registra el resultado,
y a `dvc`, que versiona el dato. Sin esto, "con que semilla y que parametros salio esto" se responde
de memoria, que es como no responderla. Gana a `argparse` —la alternativa real, no un rival
exotico— porque cada corrida deja su configuracion completa escrita en disco automaticamente, y
porque el barrido de varias combinaciones es un flag, no un bucle de shell.

Y lo que no hace bien: registrar la semilla no es fijarla. Hydra escribe `semilla: 1234` en el YAML
y se queda tan ancho; sembrar `random`, `numpy` y el marco de aprendizaje es trabajo tuyo, en la
primera linea de `main`. Un experimento con la semilla registrada y sin sembrar es exactamente igual
de irrepetible, con el agravante de que parece lo contrario.

Y una arista practica: `@hydra.main` cambia el directorio de trabajo a la carpeta de la corrida. Las
rutas relativas del codigo dejan de resolver donde esperabas — usar `hydra.utils.get_original_cwd()`
o rutas absolutas.
