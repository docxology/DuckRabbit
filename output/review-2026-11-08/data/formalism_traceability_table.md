# Formalism traceability registry

| Label | Definition and symbols | Implementation and tests | Figures and claim level |
| --- | --- | --- | --- |
| eq:typed\_request | q = (i, θ, s, e) Symbols: i, θ, s, e | Code: registry.py, schema.py; Tests: test\_generators.py | Figures: fig:architecture, fig:formalism\_traceability; Level: canonical\_stimulus |
| eq:canonical\_generation | A = Gᵢ(θ; s) Symbols: A, Gᵢ, θ, s | Code: registry.py, generators.py; Tests: test\_generators.py, test\_v03\_contracts.py | Figures: fig:architecture, fig:visual\_panel; Level: canonical\_stimulus |
| eq:canonical\_digest | c(A) = Serialize_LE,float32(A, shape, clock, units); h_c(A) = H(c(A)) Symbols: c(A), h_c, H | Code: canonical.py, manifest.py; Tests: test\_v03\_contracts.py | Figures: fig:architecture, fig:encoding\_verification; Level: physical\_metric |
| eq:encoding\_verification | F = Eₑ(A), I = D(F), V(F, M) in {verified, failed, unverified} Symbols: F, Eₑ, D, I, V, M | Code: render.py, inspection.py, manifest.py; Tests: test\_media\_and\_render.py, test\_v03\_contracts.py, test\_final\_integrity.py | Figures: fig:encoding\_verification; Level: encoded\_media |
| eq:clock\_definition | N = round(f_s T), t_k = k/f_r, Δ_AV = t_audio − t_video Symbols: N, f_s, T, t_k, f_r, Δ_AV | Code: parameters.py, artifacts.py; Tests: test\_parameters.py, test\_media\_and\_render.py | Figures: fig:temporal\_sequence, fig:audiovisual\_timeline; Level: physical\_metric |
| eq:objective\_statistics | μ_Y, σ_Y, RMS_X = M(A; units, tolerance, version) Symbols: μ_Y, σ_Y, RMS_X, M | Code: metrics.py, publication.py; Tests: test\_v04\_scholarly.py | Figures: fig:metrics\_dashboard, fig:audio\_signals; Level: physical\_metric |
| eq:temporal\_spectral\_metrics | D_k = mean  given Y_(k+1) − Y_k given ; centroid(X) = Σ fM_X(f)/max(ΣM_X(f), 1e-12); M_X = channel-mean  given rFFT(X) given  Symbols: D_k, M_X, f | Code: metrics.py, artifacts.py; Tests: test\_v04\_scholarly.py | Figures: fig:temporal\_sequence, fig:metrics\_dashboard; Level: physical\_metric |
| eq:observer\_estimand | ψ = E[Y conditional on condition and protocol] Symbols: ψ, Y, condition, protocol | Code: observer\_analysis.py, observer.py; Tests: test\_v04\_scholarly.py | Figures: fig:synthetic\_psychophysics, fig:observer\_protocol; Level: observer\_hypothesis |
| eq:synthetic\_observer | p_M(c given A_r,A_c) = σ(clip((w·φ(A_c) − w·φ(A_r))/τ, −60, 60)) Symbols: p_M, c, A_r, A_c, w, φ, τ, clip | Code: synthetic\_psychophysics.py, metrics.py; Tests: test\_synthetic\_psychophysics.py | Figures: fig:synthetic\_psychophysics; Level: synthetic\_model\_output |

: Formal definitions connect implementation and tests without converting engineering traceability into empirical evidence. {#tbl:formalism}
