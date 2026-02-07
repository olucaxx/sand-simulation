# simulador de areia (falling sand simulator)

![python](https://img.shields.io/badge/python-3.12-blue)
![pygame](https://img.shields.io/badge/pygame-2.x-green)
![repo size](https://img.shields.io/github/repo-size/olucaxx/falling-sand)

## sobre o projeto

simulador de areia inspirado no *Coding Challenge #180 – Falling Sand* do The Coding Train, desenvolvido com o objetivo de praticar lógica de simulação, renderização eficiente, manipulação de arrays e a própria biblioteca do pygame.

## características principais

- uso de arrays do **NumPy** para consultas rápidas de estado
- processamento apenas de partículas **ativas**
- renderização via **Surface + PixelArray** do pygame
- lógica de queda com gravidade inspirada em **MRU**

## limitações atuais

- a simulação começa a apresentar lentidão com cerca de **~500 partículas ativas** simultaneamente
	- o gargalo está principalmente no loop de atualização, com a verificação de colisão da gravidade 

## possíveis melhorias

- otimizar ainda mais a estrutura de dados das partículas
- aplicar multithreading ou paralelismo 
- explorar técnicas de chunking / regiões ativas

## requisitos

- **Python 3.12** 
    - versões mais recentes apresentam problemas de compatibilidade com o pygame

## instalação e execução

caso tenha mais de uma versão do Python instalada, adicione a flag `-3.12` ao criar o `venv`

```bash
git clone https://github.com/olucaxx/falling-sand
cd falling-sand
python -m venv .venv 
source .venv/Scripts/activate
pip install -r requirements.txt
python sand-simulation/engine.py
```