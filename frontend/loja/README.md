# CRIAVERSO — página da loja

Landing page + catálogo da loja de impressão 3D **CRIAVERSO** (Júlia Miranda).
Site estático, sem build e sem dependências: basta abrir `index.html` ou servir a pasta.

```bash
python3 -m http.server 8000 --directory frontend/loja
# http://localhost:8000
```

## Arquivos

| Arquivo      | O que tem                                                                 |
|--------------|---------------------------------------------------------------------------|
| `index.html` | Toda a página: header, hero, serviços, catálogo (40 produtos), como funciona, sobre, a artista, CTA e rodapé |
| `styles.css` | Design system (tokens de cor, tipografia, componentes, responsivo)         |
| `app.js`     | Filtros do catálogo, menu mobile, céu estrelado e reveal ao rolar          |
| `fonts.css`  | Poppins e Manrope embutidas em base64 — a página funciona offline          |
| `img/`       | Arte da marca e avatar da Júlia, recortados da imagem original             |

## Antes de publicar

1. **Telefone do WhatsApp.** Todos os links usam o número de exemplo `5599999999999`.
   Troque de uma vez só (formato: 55 + DDD + número):

   ```bash
   sed -i 's/5599999999999/5598999998888/g' frontend/loja/index.html
   ```

2. **Contatos do rodapé.** `(00) 00000-0000`, `contato@criaverso.com.br` e `@criaverso3d`
   são exemplos — ajuste no bloco `<ul class="f-contact">` do `index.html`.

3. **Fotos reais.** Cada produto usa uma ilustração vetorial inline (`<svg>` dentro de
   `.p-art`). Para usar foto da peça impressa, troque o `<svg>…</svg>` por
   `<img src="fotos/nome.jpg" alt="…">` — o CSS de `.p-art` já cuida do enquadramento.

4. **A biografia da Júlia é um rascunho.** O texto da seção `#artista` ("Comecei
   imprimindo miniaturas…") foi escrito como ponto de partida, não a partir da
   história real dela. Vale substituir pelas palavras da própria Júlia — é o trecho
   da página onde a voz da pessoa faz mais diferença.

## Seção "A artista"

`#artista` fica logo depois do `#sobre` e usa duas imagens em `img/`, ambas recortadas
da arte original da marca:

- `julia-miranda.jpg` (820 px) — a arte completa, dentro de uma moldura arredondada;
- `julia-avatar.jpg` (200 px) — recorte do rosto, usado no card de citação e na
  assinatura ao pé da seção.

Para trocar por uma foto real da Júlia, basta substituir os dois arquivos mantendo os
nomes (a arte funciona melhor em retrato, perto de 4:5; o avatar precisa ser quadrado).

## Catálogo

Os 40 produtos ficam em `<div class="grid" id="grid">`, um `<article class="p-card">` cada.
Para incluir ou editar uma peça, copie um card e ajuste:

- `data-cat` — `miniaturas`, `brinquedos` ou `amenidades` (é o que os filtros usam);
- `<h3>`, `.p-meta` e `.p-price` — nome, material/medida e preço;
- `.badge` — opcional: `b-best` (mais vendido), `b-new` (novidade), `b-pers` (personalizável);
- o `href` do botão **Orçar**, que já leva o nome do produto na mensagem do WhatsApp.

O contador ao lado dos filtros se atualiza sozinho.

## Identidade visual

Cores e tipos ficam nas variáveis do `:root` em `styles.css` — mudando ali, muda a página inteira.

| Token           | Valor     | Uso                          |
|-----------------|-----------|------------------------------|
| `--bg0`         | `#06030C` | fundo (quase preto violáceo) |
| `--vio` / `--mag` | `#8B5CF6` / `#C05CF7` | violeta da marca |
| `--blu`         | `#3B82F6` | azul do fim do gradiente     |
| `--grad`        | magenta → violeta → azul | logo, botões, destaques |

Tipografia: **Poppins** (títulos, o mesmo peso arredondado da marca) e **Manrope** (texto).
O símbolo do "C" com anel orbital, a estrela e o cubo são SVG desenhados no próprio HTML —
não dependem de imagem externa e escalam sem perder nitidez.
