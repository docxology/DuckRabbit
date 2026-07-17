# Formalism traceability registry

| Label | Definition and symbols | Implementation and tests | Figures and claim level |
| --- | --- | --- | --- |
| eq:typed request | q = (i, θ, s, e) Symbols: i, θ, s, e | Code: registry.py, schema.py; Tests: test generators.py | Figures: fig:architecture, fig:formalism traceability; Level: canonical stimulus |
| eq:canonical generation | A = Gᵢ(θ; s) Symbols: A, Gᵢ, θ, s | Code: registry.py, generators.py; Tests: test generators.py, test v03 contracts.py | Figures: fig:architecture, fig:visual panel; Level: canonical stimulus |
| eq:canonical digest | c(A) = Serialize_LE,float32(A, shape, clock, units); h_c(A) = H(c(A)) Symbols: c(A), h_c, H | Code: canonical.py, manifest.py; Tests: test v03 contracts.py | Figures: fig:architecture, fig:encoding verification; Level: physical metric |
| eq:encoding verification | F = Eₑ(A), I = D(F), V(F, M) ∈ {pass, fail} Symbols: F, Eₑ, D, I, V, M | Code: render.py, inspection.py, manifest.py; Tests: test media and render.py, test v03 contracts.py | Figures: fig:encoding verification; Level: encoded media |
| eq:clock definition | N = round(f_s T), t_k = k/f_r, Δ_AV = t_audio − t_video Symbols: N, f_s, T, t_k, f_r, Δ_AV | Code: parameters.py, artifacts.py; Tests: test parameters.py, test media and render.py | Figures: fig:temporal sequence, fig:audiovisual timeline; Level: physical metric |
| eq:objective statistics | μ_Y, σ_Y, RMS_X = M(A; units, tolerance, version) Symbols: μ_Y, σ_Y, RMS_X, M | Code: metrics.py, publication.py; Tests: test v04 scholarly.py | Figures: fig:metrics dashboard, fig:audio signals; Level: physical metric |
| eq:temporal spectral metrics | D_k = mean absolute difference of adjacent frames; centroid(X) = Σ fP_X(f)/ΣP_X(f) Symbols: D_k, P_X, f | Code: metrics.py, artifacts.py; Tests: test v04 scholarly.py | Figures: fig:temporal sequence, fig:metrics dashboard; Level: physical metric |
| eq:observer estimand | ψ = E[Y conditional on condition and protocol] Symbols: ψ, Y, condition, protocol | Code: observer analysis.py, observer.py; Tests: test v04 scholarly.py | Figures: fig:synthetic psychophysics, fig:observer protocol; Level: observer hypothesis |
| eq:synthetic observer | p_M(c given A_r,A_c) = σ((w·φ(A_c) − w·φ(A_r))/τ) Symbols: p_M, c, A_r, A_c, w, φ, τ | Code: synthetic psychophysics.py, metrics.py; Tests: test synthetic psychophysics.py | Figures: fig:synthetic psychophysics; Level: synthetic model output |

: Formal definitions connect implementation and tests without converting engineering traceability into empirical evidence. {#tbl:formalism}
