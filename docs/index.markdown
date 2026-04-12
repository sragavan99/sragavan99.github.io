---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

![headshot](assets/headshot.jpg){: height="200px" width="230px" style="float:left; padding-right:20px" }

Welcome! I am a third-year PhD student at MIT, where I am very fortunate to be advised by [Vinod Vaikuntanathan](https://people.csail.mit.edu/vinodv). I am broadly interested in theoretical computer science, particularly quantum algorithms, coding theory, and cryptography.

Previously, I worked as a quantitative research analyst at Citadel Securities. Before that, I completed my undergraduate degree in mathematics at Princeton University in 2021, where I had the pleasure of being advised by [Matt Weinberg](https://www.cs.princeton.edu/~smattw/). See my [CV](CV.markdown) for more information.

Email: first initial last name at mit dot edu

<br/>
## Recent News
- _April 2026:_ I will be [speaking](https://www.ias.edu/math/events/computer-sciencediscrete-mathematics-seminar-i-621) at the Institute for Advanced Study in Princeton on catalytic algorithms for tree evaluation.
- _February 2026:_ I gave a talk at the BU Security Seminar on [constructions](https://eprint.iacr.org/2025/2008) and [applications](https://eccc.weizmann.ac.il/report/2026/022/) of information-theoretic private information retrieval. Slides are available [here](slides/bu26-pir.pdf).
- _February 2026:_ [Alexandra Henzinger](https://people.csail.mit.edu/ahenz/), [Ted Pyne](https://sites.google.com/view/tedpyne/), and I uploaded a [manuscript](https://eccc.weizmann.ac.il/report/2026/022/) drawing a connection between information-theoretic private information retrieval and the tree evaluation problem. See pages 183-198 of [these slides](slides/bu26-pir.pdf) for a teaser!
- _December 2025:_ [Sid Jain](https://sidjain.me/), [Sascha Schmidhuber](https://www.mit.edu/~alexsc/), [Noah Shutty](https://research.google/people/noahshutty/), and I recently organised a workshop at [FOCS 2025](https://focs.computer.org/2025/) on [Breaking and Making Quantum Speedups](https://sites.google.com/view/quantumfocs2025/home).
- _November 2025:_ I'm very excited to be interning at [Google Quantum AI](https://quantumai.google/) with [Noah Shutty](https://research.google/people/noahshutty/) in summer 2026!

<br/>
## Resources
If you are interested in learning about quantum algorithms, I hope some of the below slides might be useful!
- [Sid Jain](https://sidjain.me/) and I gave an introductory tutorial for a [workshop](https://sites.google.com/view/quantumfocs2025/home) at FOCS 2025. We start from classic ideas underlying Shor's integer factoring algorithm and Grover's search algorithm, and outline how principles from these have been extended to yield new quantum algorithms in recent years. Slides are available [here](slides/focs25-workshop-tutorial.pdf).
- For a less technical and higher-level overview of what we know about quantum algorithms for factoring integers, see [these slides](slides/cryptoday25-factoring-sota.pdf) or [this video recording](https://www.youtube.com/watch?v=TVev-BYtPX8&ab_channel=MITSchwarzmanCollegeofComputing).
- If you are a mathematician or number theorist, you might find [these slides](slides/unsw25-jacobi.pdf) more beneficial. A key open problem highlighted here is that of finding better classical algorithms for factoring integers of the form $N = P^2Q$ where $P, Q$ are primes and $Q \ll P$. As far as I know, the current state of the art is due to [this paper](https://arxiv.org/abs/2308.06130) by Erik Mulder.

<br/>
# Publications

**Two-Server Private Information Retrieval in Sublinear Time and Quasilinear Space** [[ePrint]](https://eprint.iacr.org/2025/2008) [[code]](https://github.com/ahenzinger/finite-diffs-pir)<br/>
with [Alexandra Henzinger](https://people.csail.mit.edu/ahenz/)<br/>
Eurocrypt 2026<br/>

**Parallel Spooky Pebbling Makes Regev Factoring More Practical** [[arXiv]](https://www.arxiv.org/abs/2510.08432) [[ePrint]](https://eprint.iacr.org/2025/1887) [[code]](https://github.com/GregDMeyer/parallel-spooky-pebbling)<br/>
with [Greg Kahanamoku-Meyer](https://gregkm.me/) and Katherine Van Kirk<br/>
Eurocrypt 2026, QIP 2026<br/>

**Cloning Games, Black Holes and Cryptography** [[arXiv]](https://arxiv.org/abs/2411.04730) [[ePrint]](https://eprint.iacr.org/2024/1826) [[ITCS]](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.109) <br/>
with [Alex Poremba](https://scc1.bu.edu/poremba/) and [Vinod Vaikuntanathan](https://people.csail.mit.edu/vinodv)<br/>
ITCS 2026, QIP 2026<br/>

**The Jacobi Factoring Circuit: Quantum Factoring with Near-Linear Gates and Sublinear Space and Depth** [[arXiv]](https://arxiv.org/abs/2412.12558) [[ePrint]](https://eprint.iacr.org/2024/2034) [[STOC]](https://dl.acm.org/doi/10.1145/3717823.3718273)<br/>
with [Greg Kahanamoku-Meyer](https://gregkm.me/), [Vinod Vaikuntanathan](https://people.csail.mit.edu/vinodv), and Katherine Van Kirk<br/>
STOC 2025, QIP 2026<br/>
Featured on [Lakshmi Chandrasekaran's blog](https://scieye.wordpress.com/2025/06/07/beyond-cryptography-the-use-of-factorization-to-evaluate-the-power-of-a-quantum-computer/)<br/>

**Indistinguishability Obfuscation from Bilinear Maps and LPN Variants** [[ePrint]](https://eprint.iacr.org/2024/856) [[TCC]](https://link.springer.com/chapter/10.1007/978-3-031-78023-3_1)<br/>
with [Neekon Vafa](https://neekonvafa.com/) and [Vinod Vaikuntanathan](https://people.csail.mit.edu/vinodv)<br/>
TCC 2024<br/>
Featured on [Lakshmi Chandrasekaran's blog](https://scieye.wordpress.com/2026/01/15/constructing-indistinguishability-obfuscation-schemes-in-a-hardness-rich-world/)<br/>

**Space-Efficient and Noise-Robust Quantum Factoring** [[Journal of Cryptology]](https://link.springer.com/article/10.1007/s00145-026-09572-x) [[public PDF link]](https://rdcu.be/e2mnc)<br/>
with [Vinod Vaikuntanathan](https://people.csail.mit.edu/vinodv)<br/>
Journal of Cryptology, merge of the following two papers:
- **Space-Efficient and Noise-Robust Quantum Factoring** [[arXiv]](https://arxiv.org/abs/2310.00899) [[ePrint]](https://eprint.iacr.org/2023/1501) [[CRYPTO]](https://link.springer.com/chapter/10.1007/978-3-031-68391-6_4)<br/>
  CRYPTO 2024<br/>
  **Best Paper Award**<br/>
  Mentioned in [Quanta Magazine](https://www.quantamagazine.org/thirty-years-later-a-speed-boost-for-quantum-factoring-20231017/) and [MIT News](https://news.mit.edu/2024/toward-code-breaking-quantum-computer-0823)<br/>
- **Regev Factoring Beyond Fibonacci: Optimizing Prefactors** [[ePrint]](https://eprint.iacr.org/2024/636)<br/>

**On the cut-query complexity of approximating max-cut** [[arXiv]](https://arxiv.org/abs/2211.04506) [[ICALP]](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2024.115)<br/>
with Orestis Plevrakis and [Matt Weinberg](https://www.cs.princeton.edu/~smattw/)<br/>
ICALP 2024<br/>

**A proof of the triangular Ashbaugh-Benguria-Payne–Pólya–Weinberger inequality** [[arXiv]](https://arxiv.org/abs/2009.00927) [[JST]](https://ems.press/journals/jst/articles/7525210) [[code]](https://github.com/sragavan99/triangle-ppw-inequality) <br/>
with Ryan Arbon, Mohammed Mannan, and [Michael Psenka](https://www.michaelpsenka.io/)<br/>
Journal of Spectral Theory, 2022<br/>

**Morphology-Aware Meta-Embeddings for Tamil** [[NAACL]](https://aclanthology.org/2021.naacl-srw.13/)<br/>
with Arjun Sai Krishnan<br/>
NAACL Student Research Workshop, 2021<br/>

<br/>
# Manuscripts

**Catalytic Tree Evaluation From Matching Vectors** [[arXiv]](https://arxiv.org/abs/2602.14320) [[ECCC]](https://eccc.weizmann.ac.il/report/2026/022/) [[ePrint]](https://eprint.iacr.org/2026/265)<br/>
with [Alexandra Henzinger](https://people.csail.mit.edu/ahenz/) and [Ted Pyne](https://sites.google.com/view/tedpyne/)<br/>

<br/>
# Talks

**Parallel Spooky Pebbling Makes Regev Factoring More Practical** [[slides made jointly with Greg and Katherine]](slides/quera26-spooky-pebbling.pdf)
- QuEra Computing (March 2026)

**Quantum Algorithms, Old and New** [[slides]](slides/focs25-workshop-tutorial.pdf)
- FOCS 2025, tutorial for a workshop on [Breaking and Making Quantum Speedups](https://sites.google.com/view/quantumfocs2025/home) (December 2025, with [Sid Jain](https://sidjain.me/))

**Two-Server Private Information Retrieval in Sublinear Time and Quasilinear Space** [[latest slides]](slides/bu26-pir.pdf)
- Boston University Security Seminar (February 2026, [slides](slides/bu26-pir.pdf))
- MIT CIS Seminar (November 2025, with [Alexandra Henzinger](https://people.csail.mit.edu/ahenz/), [slides](slides/cisf25-2pir.pdf))
- MIT Simple Person's Applied Mathematics Seminar (October 2025)

**The Jacobi Factoring Circuit: Classically Hard Factoring in Sublinear Quantum Space and Depth** [[latest slides]](slides/iqmvt26-jacobi.pdf)
- Virginia Tech Quantum Seminar (February 2026, [slides](slides/iqmvt26-jacobi.pdf))
- IQM Quantum Machine Learning Seminar (February 2026, [slides](slides/iqmvt26-jacobi.pdf))
- QIP 2026 (January 2026, with Katherine Van Kirk, [slides](slides/qip26-jacobi.pdf))
- Tufts Quantum Computing Seminar (September 2025)
- UNSW Number Theory Days (August 2025, [slides](slides/unsw25-jacobi.pdf))
- Ruhr University Bochum Quantum Information Workshop (April 2025)
- Simons Institute Quantum Colloquium (March 2025, [slides](slides/simons25-jacobi.pdf), [video](https://www.youtube.com/watch?v=TA32tEow2Ug&list=PLgKuh-lKre11rEOFaO62MJCzBXfjZSDqA&index=1&ab_channel=SimonsInstitute))
- MIT Quantum Information Seminar (March 2025)
- CMU Theory Seminar (March 2025)

**Cloning Games, Black Holes and Cryptography** [[slides]](slides/qip26-cloning.pdf)
- QIP 2026 (January 2026)
- Kyoto University Quantum Cryptography Workshop (October 2025, [video](https://www2.yukawa.kyoto-u.ac.jp/~tomoyuki.morimae/KyotoQcrypt2/Ragavan.mp4))
- CMU CyLab Crypto Seminar (March 2025, [video](https://youtu.be/-T_9OLcJ9a8))

**Factoring with a Quantum Computer: The State of the Art** [[latest slides]](slides/uts25-factoring-sota.pdf)
- University of Technology Sydney (August 2025, [slides](slides/uts25-factoring-sota.pdf))
- University of Sydney (August 2025)
- QuEra Computing (April 2025, with [Greg Kahanamoku-Meyer](https://gregkm.me/) and Katherine Van Kirk)
- MIT Schwarzman College of Computing Cryptography and Security Day (January 2025, [slides](slides/cryptoday25-factoring-sota.pdf), [video](https://www.youtube.com/watch?v=TVev-BYtPX8&ab_channel=MITSchwarzmanCollegeofComputing))

**Indistinguishability Obfuscation from Bilinear Maps and LPN Variants** [[slides]](slides/cisf24-io.pdf)
- MIT CIS Seminar (September 2024)

**Space-Efficient and Noise-Robust Quantum Factoring** [[slides]](slides/crypto24-factoring.pdf)
- CRYPTO 2024 (August 2024)
- IBM Quantum Seminar (November 2023)
- Yale Quantum Institute (November 2023)

**The Cut-Query Complexity of Approximating Max-Cut** [[slides]](slides/icalp24-maxcut.pdf)
- ICALP 2024 (July 2024)

<br/>
# Teaching and Service

- Program Committee Member, [QIP 2026](https://qip2026.lu.lv/)
- Teaching Assistant, 6.1200 Mathematics for Computer Science (MIT, Fall 2025)
- Teaching Assistant, COS 445 Economics and Computing (Princeton, Spring 2019)