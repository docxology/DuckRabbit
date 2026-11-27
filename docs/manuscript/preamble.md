# LaTeX Preamble

This file contains LaTeX packages and commands that are automatically injected into the document compilation process.

The [publication guide](../publication.md#render-with-the-pinned-template)
records the render command used with this preamble.

```latex
% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}
\newtheorem{remark}{Remark}
\newtheorem{example}{Example}
\newtheorem{theorem}{Theorem}

% Document layout
\usepackage{geometry}
\geometry{margin=0.6in}
\usepackage{float}
\usepackage{graphicx}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}

% Code listings
\usepackage{listings}

% Typography and formatting
\usepackage{microtype}
\usepackage{xcolor}

% Cross-references and citations
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=[rgb]{0.10,0.25,0.55},
    citecolor=[rgb]{0.10,0.25,0.55},
    urlcolor=[rgb]{0.10,0.35,0.65}
}
\usepackage[capitalise,noabbrev]{cleveref}
\usepackage{natbib}

% Prefer the intended typeface when installed. Use a Unicode fallback otherwise.
\IfFontExistsTF{JuliaMono}{%
  \setmonofont{JuliaMono}[Scale=MatchLowercase]%
}{%
  \IfFontExistsTF{DejaVu Sans Mono}{%
    \setmonofont{DejaVu Sans Mono}[Scale=MatchLowercase]%
  }{}%
}

% Math font for unicode-math: Latin Modern Math (TeX Live) has full BMP
% coverage including U+2223 (\mid), U+226A/226B (\ll/\gg), and the Greek/
% blackboard letters used in equations. Without an explicit \setmathfont,
% unicode-math falls back to lmroman text font which lacks several glyphs
% and emits "Missing character" warnings on every \mid in math mode.
\setmathfont{latinmodern-math.otf}
```
