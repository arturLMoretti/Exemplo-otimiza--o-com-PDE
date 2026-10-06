# ⚠️ ESTE REPOSITÓRIO PODE SER REMOVIDO

> **Não há mais nada a manter aqui.** O código foi copiado para
> **[`arturLMoretti/adsorptionKinectsAndEquilibriumModelling`](https://github.com/arturLMoretti/adsorptionKinectsAndEquilibriumModelling)**,
> branch **`ccr-80b00589-jlbrwb`** (commit `942a857`), em `cpp/pde_particula/`.
> Os arquivos foram retirados deste branch para evitar duas fontes da verdade.

## O que havia aqui

Exemplo em **C++17 + Python** de estimação de parâmetros de uma PDE de **adsorção em partícula
esférica**: difusão radial com isoterma de Langmuir e filme externo, otimização por Nelder-Mead
(`D_eff`, `k_L`, `q_max`, `k_f`), dados sintéticos, gráficos e relatório em LaTeX (out/2025,
2 commits).

## O que foi feito

* Todo o código (`adsorption_optimization.*`, `exemplo_adsorcao*.cpp`, `Makefile`, scripts de
  gráficos e relatório, `config.ini` e a documentação) foi copiado **sem alterações numéricas** para
  `cpp/pde_particula/` no repositório consolidado, com uma `NOTA.md` sobre o estado do código.
* O CI do repositório consolidado passou a compilar o C++.
* Não foi levado o binário compilado `exemplo_adsorcao` (gerado pelo `make`) nem o `.gitignore`.

## ⚠️ O modelo completo não adsorve

Compilado e executado, `./exemplo_adsorcao` termina com **uptake final ≈ 4·10⁻¹⁵⁷ kg/kg**, ou seja,
nenhuma adsorção. O "ajuste" (RMSE ≈ 1·10⁻⁵) é feito contra dados sintéticos gerados pelo próprio
modelo, então não detecta o problema. Pontos que merecem revisão (por leitura do código):

* `C_ext = C_0·exp(−0,1·t)` é imposto, sem balanço de massa no líquido;
* a linearização de Langmuir em `solve_pde_step` (termos `dt·ρp·(q − C·q')`) não corresponde à
  discretização de `ρp ∂q/∂t`;
* o README descrevia `ρp(1−ε)·∂q/∂t`, mas o código usa só `ρp`.

O mesmo problema físico (difusão em esfera, banho finito, filme externo, estimação de parâmetros)
está implementado e **validado** em Python no repositório consolidado
(`src/adsorcao/cinetica/sdm.py`, comparado com a solução analítica de Crank). **Prefira-o.**

## Antes de remover

* O histórico completo continua no git; o último commit com os arquivos é `cff9866`
  (`git checkout cff9866`). **Remover o repositório apaga esse histórico.**
* Este repositório só tem o branch `master`.
* O código consolidado está num **branch** (`ccr-80b00589-jlbrwb`) ainda **não** mesclado ao
  `master` do repositório consolidado. Mescle (ou faça fork) antes de apagar qualquer coisa.
