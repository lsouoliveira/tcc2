# Getting Started

Edite os scripts de cada algoritmo para configurá-los de acordo com sua rede.

Edite `run_project.sh` para escolher os algoritmos que serão executados e quais
tráfegos serão gerados.

```sh
sudo ./run.sh [FATTREE-K] [CORES] [NUM_FLOWS] [DURATION]
```

Exemplo:

```sh
sudo ./run.sh 4 2.0 1 1
```

> Os algoritmos serão executados para cada tráfego escolhido durante o período
estabelecido.

Quando a execução dos algoritmos terminar, os resultados gerados estarão na
pasta `results`.

Edite o arquivo `plot_results.py` para escolher quais gráficos serão gerados.

Gere o gráfico com os resultados usando o seguinte comando:

```sh
sudo ./plot.sh [FATTREE-K] [CORES] [NUM_FLOWS] [DURATION]
```

Exemplo:

```sh
sudo ./plot.sh 4 2.0 1 1
```

Os gráficos gerados estarão em `results`. Uma imagem para cada gráfico.
